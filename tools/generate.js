const axios = require('axios');
const fs = require('fs');
const path = require('path');
const Handlebars = require('handlebars');

/**
 * URL endpoint JSON dari Google Apps Script
 */
const SHEETS_URL = 'https://script.google.com/macros/s/AKfycbzk7H09i-P5_5wPc82mgr53poH-3wtJi8kEe3eIsTqHmcdutsT-T1sPgnA5qx1SLtzpSg/exec';

// Paths
const TEMPLATE_PATH = path.join(__dirname, 'template.html');
const ARTICLES_JSON_PATH = path.resolve(__dirname, '../articles.json');
const OUT_DIR = path.resolve(__dirname, '../article');
const IMG_DIR = 'img'; // Path relatif dari root

/**
 * Utility: convert string to slug
 */
function toSlug(str) {
  if (!str) return 'unknown';
  return str
    .toString()
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '');
}

/**
 * Backup articles.json
 */
function backupArticlesJson() {
  const timestamp = Math.floor(Date.now() / 1000);
  const backupPath = `${ARTICLES_JSON_PATH}.bak.${timestamp}`;
  if (fs.existsSync(ARTICLES_JSON_PATH)) {
    fs.copyFileSync(ARTICLES_JSON_PATH, backupPath);
    console.log(`✅ Backup articles.json: ${path.basename(backupPath)}`);
  }
}

/**
 * Read existing articles.json
 */
function readExistingArticles() {
  try {
    if (fs.existsSync(ARTICLES_JSON_PATH)) {
      const data = fs.readFileSync(ARTICLES_JSON_PATH, 'utf8');
      return JSON.parse(data);
    }
  } catch (err) {
    console.warn(`⚠️  Error reading articles.json:`, err.message);
  }
  return [];
}

/**
 * Main generator
 */
async function generateArticles() {
  try {
    console.log('📥 Mengambil data dari Google Sheets...');
    const response = await axios.get(SHEETS_URL, { timeout: 10000 });
    const newArticles = response.data;

    if (!Array.isArray(newArticles) || newArticles.length === 0) {
      console.warn('⚠️  Data kosong atau format tidak valid.');
      return;
    }

    console.log(`📊 Ditemukan ${newArticles.length} artikel dari Sheets.`);

    // Read template
    if (!fs.existsSync(TEMPLATE_PATH)) {
      console.error(`❌ Template tidak ditemukan: ${TEMPLATE_PATH}`);
      process.exit(1);
    }
    const templateContent = fs.readFileSync(TEMPLATE_PATH, 'utf8');
    const template = Handlebars.compile(templateContent);

    // Ensure output dir exists
    if (!fs.existsSync(OUT_DIR)) {
      fs.mkdirSync(OUT_DIR, { recursive: true });
      console.log(`✅ Folder output dibuat: ${OUT_DIR}`);
    }

    // Read existing articles
    let existingArticles = readExistingArticles();
    console.log(`📖 Ditemukan ${existingArticles.length} artikel existing di articles.json`);

    // Create lookup by slug to avoid duplicates
    const existingSlugs = new Set(existingArticles.map(a => a.slug || ''));

    // Backup before update
    backupArticlesJson();

    let newCount = 0;
    let updateCount = 0;
    let skipCount = 0;

    // Process each article
    for (const sheetRow of newArticles) {
      try {
        const slug = sheetRow.slug ? toSlug(sheetRow.slug) : toSlug(sheetRow.title);
        
        if (!slug || slug === 'unknown') {
          console.warn(`⏭️  Lewati artikel (slug invalid): ${sheetRow.title}`);
          skipCount++;
          continue;
        }

        // Prepare image path
        let imagePath = '';
        if (sheetRow.image) {
          if (sheetRow.image.startsWith('http')) {
            imagePath = sheetRow.image;
          } else {
            imagePath = `${IMG_DIR}/${sheetRow.image}`;
          }
        }

        // For HTML files in article/ subfolder, prepend ../ to local image paths
        let imagePathForHTML = imagePath;
        if (imagePath && !imagePath.startsWith('http')) {
          imagePathForHTML = `../${imagePath}`;
        }
        console.log(`🖼️  [${slug}] imagePath="${imagePath}", imagePathForHTML="${imagePathForHTML}"`);

        // Auto-wrap plain text content in <p> tags if not HTML
        let processedContent = sheetRow.content || sheetRow.excerpt || '<p>Konten tidak tersedia</p>';
        if (processedContent && !processedContent.includes('<')) {
          processedContent = `<p>${processedContent.replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>')}</p>`;
        }

        // Prepare data for template
        const articleData = {
          title: sheetRow.title || 'Tanpa Judul',
          date: sheetRow.date || new Date().toISOString().split('T')[0],
          category: sheetRow.category || sheetRow.badge || 'Berita',
          badge: sheetRow.badge || sheetRow.category || 'Berita',
          image: imagePathForHTML,
          content: processedContent,
          author: sheetRow.author || '',
          excerpt: sheetRow.excerpt || (sheetRow.content || '').replace(/<[^>]*>/g, '').substring(0, 150),
          slug: slug
        };

        // Render HTML
        const html = template(articleData);

        // Write file
        const filePath = path.join(OUT_DIR, `${slug}.html`);
        fs.writeFileSync(filePath, html, 'utf8');

        // Prepare JSON entry (untuk articles.json) - use original imagePath for root-level access
        const jsonEntry = {
          title: articleData.title,
          excerpt: articleData.excerpt.replace(/<[^>]*>/g, '').substring(0, 150),
          category: articleData.category,
          date: articleData.date,
          image: imagePath,
          url: `article/${slug}.html`,
          slug: slug
        };

        // If author exists, add it
        if (articleData.author) {
          jsonEntry.author = articleData.author;
        }

        // Check if article exists (by slug)
        const existingIndex = existingArticles.findIndex(a => a.slug === slug);
        
        if (existingIndex !== -1) {
          // Update existing
          existingArticles[existingIndex] = jsonEntry;
          console.log(`🔄 Update: ${slug}.html`);
          updateCount++;
        } else {
          // Add new at beginning
          existingArticles.unshift(jsonEntry);
          console.log(`✅ Baru: ${slug}.html`);
          newCount++;
        }

      } catch (err) {
        console.error(`❌ Error memproses artikel (${sheetRow?.title}):`, err.message);
      }
    }

    // Write updated articles.json
    const jsonPath = ARTICLES_JSON_PATH;
    fs.writeFileSync(jsonPath, JSON.stringify(existingArticles, null, 2), 'utf8');
    console.log(`💾 Update ${jsonPath}`);

    // Summary
    console.log(`\n📋 Ringkasan:`);
    console.log(`   ✨ Artikel baru: ${newCount}`);
    console.log(`   🔄 Artikel update: ${updateCount}`);
    console.log(`   ⏭️  Dilewati: ${skipCount}`);
    console.log(`   📁 Total artikel di DB: ${existingArticles.length}`);
    console.log(`\n✅ Selesai! Artikel sudah siap di news.html, search.html, dan filter kategori`);

  } catch (error) {
    console.error('❌ Error fatal:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
    process.exit(1);
  }
}

// Run
generateArticles();

/**
 * Utility: convert string to slug
 */
function toSlug(str) {
  if (!str) return 'unknown';
  return str
    .toString()
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '');
}

/**
 * Backup articles.json
 */
function backupArticlesJson() {
  const timestamp = Math.floor(Date.now() / 1000);
  const backupPath = `${ARTICLES_JSON_PATH}.bak.${timestamp}`;
  if (fs.existsSync(ARTICLES_JSON_PATH)) {
    fs.copyFileSync(ARTICLES_JSON_PATH, backupPath);
    console.log(`✅ Backup articles.json: ${path.basename(backupPath)}`);
  }
}

/**
 * Read existing articles.json
 */
function readExistingArticles() {
  try {
    if (fs.existsSync(ARTICLES_JSON_PATH)) {
      const data = fs.readFileSync(ARTICLES_JSON_PATH, 'utf8');
      return JSON.parse(data);
    }
  } catch (err) {
    console.warn(`⚠️  Error reading articles.json:`, err.message);
  }
  return [];
}

/**
 * Main generator
 */
async function generateArticles() {
  try {
    console.log('📥 Mengambil data dari Google Sheets...');
    const response = await axios.get(SHEETS_URL, { timeout: 10000 });
    const newArticles = response.data;

    if (!Array.isArray(newArticles) || newArticles.length === 0) {
      console.warn('⚠️  Data kosong atau format tidak valid.');
      return;
    }

    console.log(`📊 Ditemukan ${newArticles.length} artikel dari Sheets.`);

    // Read template
    if (!fs.existsSync(TEMPLATE_PATH)) {
      console.error(`❌ Template tidak ditemukan: ${TEMPLATE_PATH}`);
      process.exit(1);
    }
    const templateContent = fs.readFileSync(TEMPLATE_PATH, 'utf8');
    const template = Handlebars.compile(templateContent);

    // Ensure output dir exists
    if (!fs.existsSync(OUT_DIR)) {
      fs.mkdirSync(OUT_DIR, { recursive: true });
      console.log(`✅ Folder output dibuat: ${OUT_DIR}`);
    }

    // Read existing articles
    let existingArticles = readExistingArticles();
    console.log(`📖 Ditemukan ${existingArticles.length} artikel existing di articles.json`);

    // Create lookup by slug to avoid duplicates
    const existingSlugs = new Set(existingArticles.map(a => a.slug || ''));

    // Backup before update
    backupArticlesJson();

    let newCount = 0;
    let updateCount = 0;
    let skipCount = 0;

    // Process each article
    for (const sheetRow of newArticles) {
      try {
        const slug = sheetRow.slug ? toSlug(sheetRow.slug) : toSlug(sheetRow.title);
        
        if (!slug || slug === 'unknown') {
          console.warn(`⏭️  Lewati artikel (slug invalid): ${sheetRow.title}`);
          skipCount++;
          continue;
        }

        // Prepare image path
        let imagePath = '';
        if (sheetRow.image) {
          if (sheetRow.image.startsWith('http')) {
            imagePath = sheetRow.image;
          } else {
            imagePath = `${IMG_DIR}/${sheetRow.image}`;
          }
        }

        // For HTML files in article/ subfolder, prepend ../ to local image paths
        let imagePathForHTML = imagePath;
        if (imagePath && !imagePath.startsWith('http')) {
          imagePathForHTML = `../${imagePath}`;
        }
        console.log(`🖼️  [${slug}] imagePath="${imagePath}", imagePathForHTML="${imagePathForHTML}"`);

        // Auto-wrap plain text content in <p> tags if not HTML
        let processedContent = sheetRow.content || sheetRow.excerpt || '<p>Konten tidak tersedia</p>';
        if (processedContent && !processedContent.includes('<')) {
          processedContent = `<p>${processedContent.replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>')}</p>`;
        }

        // Prepare data for template
        const articleData = {
          title: sheetRow.title || 'Tanpa Judul',
          date: sheetRow.date || new Date().toISOString().split('T')[0],
          badge: sheetRow.badge || sheetRow.category || 'Berita',
          category: sheetRow.category || 'Umum',
          image: imagePathForHTML,
          content: processedContent,
          author: sheetRow.author || '',
          excerpt: sheetRow.excerpt || (sheetRow.content || '').substring(0, 150),
          slug: slug
        };

        // Render HTML
        const html = template(articleData);

        // Write file
        const filePath = path.join(OUT_DIR, `${slug}.html`);
        fs.writeFileSync(filePath, html, 'utf8');

        // Prepare JSON entry - use original imagePath for root-level access
        const jsonEntry = {
          title: articleData.title,
          excerpt: articleData.excerpt.replace(/<[^>]*>/g, '').substring(0, 150),
          category: articleData.category,
          date: articleData.date,
          image: imagePath,
          url: `article/${slug}.html`,
          slug: slug,
          author: articleData.author || undefined
        };

        // Remove undefined author
        if (!jsonEntry.author) delete jsonEntry.author;

        // Check if article exists (by slug)
        const existingIndex = existingArticles.findIndex(a => a.slug === slug);
        
        if (existingIndex !== -1) {
          // Update existing
          existingArticles[existingIndex] = jsonEntry;
          console.log(`🔄 Update: ${slug}.html`);
          updateCount++;
        } else {
          // Add new at beginning
          existingArticles.unshift(jsonEntry);
          console.log(`✅ Baru: ${slug}.html`);
          newCount++;
        }

      } catch (err) {
        console.error(`❌ Error memproses artikel (${sheetRow?.title}):`, err.message);
      }
    }

    // Write updated articles.json
    const jsonPath = ARTICLES_JSON_PATH;
    fs.writeFileSync(jsonPath, JSON.stringify(existingArticles, null, 2), 'utf8');
    console.log(`💾 Update ${jsonPath}`);

    // Summary
    console.log(`\n📋 Ringkasan:`);
    console.log(`   ✨ Artikel baru: ${newCount}`);
    console.log(`   🔄 Artikel update: ${updateCount}`);
    console.log(`   ⏭️  Dilewati: ${skipCount}`);
    console.log(`   📁 Total artikel di DB: ${existingArticles.length}`);
    console.log(`\n✅ Selesai! Artikel sudah siap di news.html & search.html`);

  } catch (error) {
    console.error('❌ Error fatal:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
    process.exit(1);
  }
}

// Run
generateArticles();
