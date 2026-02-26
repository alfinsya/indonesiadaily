#!/usr/bin/env node

/**
 * Script untuk Generate 34 Portal Berita dari Template BizNews
 * 
 * Usage:
 *   node generate-sites.js
 * 
 * Script ini akan:
 * 1. Membaca sites-config.json
 * 2. Untuk setiap site:
 *    - Copy folder BizNews ke folder baru
 *    - Replace string di semua file:
 *      * Nama portal berita
 *      * Email
 *      * Handle social media
 *      * Warna tema (primary, dark, secondary)
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Color codes untuk terminal
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(color, message) {
  console.log(`${colors[color] || colors.reset}${message}${colors.reset}`);
}

// Load config
const configPath = path.join(__dirname, 'sites-config.json');
let config;

try {
  config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  log('green', '✓ Config loaded successfully');
} catch (error) {
  log('red', `✗ Error loading config: ${error.message}`);
  process.exit(1);
}

// Base path untuk semua folder
const baseDir = path.resolve(__dirname, '..');
const originalFolder = path.join(baseDir, config.originalFolder);

// Validasi folder original
if (!fs.existsSync(originalFolder)) {
  log('red', `✗ Original folder not found: ${originalFolder}`);
  process.exit(1);
}

log('blue', `\n🚀 Starting generation of ${config.sites.length} portal berita...\n`);

/**
 * Copy folder recursively
 */
function copyFolderSync(src, dest) {
  const exists = fs.existsSync(src);
  const stats = exists && fs.statSync(src);
  const isDirectory = exists && stats.isDirectory();

  if (isDirectory) {
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest, { recursive: true });
    }
    fs.readdirSync(src).forEach((childItemName) => {
      copyFolderSync(path.join(src, childItemName), path.join(dest, childItemName));
    });
  } else {
    fs.copyFileSync(src, dest);
  }
}

/**
 * Recursive file replacement
 */
function replaceInFiles(dir, replacements, fileExtensions = ['.html', '.css', '.js', '.json']) {
  const files = fs.readdirSync(dir);

  files.forEach((file) => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      // Skip backup dan node_modules
      if (!file.startsWith('.') && file !== 'node_modules' && !file.includes('.bak')) {
        replaceInFiles(filePath, replacements, fileExtensions);
      }
    } else if (stat.isFile()) {
      const ext = path.extname(file).toLowerCase();
      if (fileExtensions.includes(ext)) {
        try {
          let content = fs.readFileSync(filePath, 'utf8');
          let hasChanged = false;

          for (const [search, replace] of Object.entries(replacements)) {
            const regex = new RegExp(search.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
            if (regex.test(content)) {
              content = content.replace(regex, replace);
              hasChanged = true;
            }
          }

          if (hasChanged) {
            fs.writeFileSync(filePath, content, 'utf8');
          }
        } catch (error) {
          log('yellow', `⚠ Error processing ${filePath}: ${error.message}`);
        }
      }
    }
  });
}

/**
 * Generate satu site
 */
function generateSite(siteConfig, index) {
  const totalSites = config.sites.length;
  const progress = `[${index}/${totalSites}]`;

  try {
    log('cyan', `\n${progress} Generating: ${siteConfig.siteName}`);
    
    const targetFolder = path.join(baseDir, siteConfig.folderName);

    // 1. Copy folder
    log('yellow', `  → Copying folder...`);
    if (fs.existsSync(targetFolder)) {
      log('yellow', `    (removing existing folder)`);
      fs.rmSync(targetFolder, { recursive: true, force: true });
    }
    copyFolderSync(originalFolder, targetFolder);

    // 2. Define replacement rules
    const replacements = {
      // Nama portal/brand
      'BizNews': siteConfig.siteName,
      'IndonesiaDaily': siteConfig.siteName.replace(/[^a-zA-Z0-9]/g, ''),
      'indonesiadaily': siteConfig.socialHandle.toLowerCase(),
      'PORTAL_NAME': siteConfig.siteName,
      
      // Email
      'IndonesiaDaily33@gmail.com': siteConfig.email,
      'indonesia.daily.33@gmail.com': siteConfig.email,
      
      // About Us descriptions
      'TENTANG KAMI - PLACEHOLDER': `TENTANG ${siteConfig.siteName.toUpperCase()}`,
      
      // Warna-warna CSS
      '--primary: #FFCC00': `--primary: ${siteConfig.colors.primary}`,
      '--dark: #1E2024': `--dark: ${siteConfig.colors.dark}`,
      '--secondary: #31404B': `--secondary: ${siteConfig.colors.secondary}`,
      
      // Warna dalam inline styles
      'background: #FFCC00': `background: ${siteConfig.colors.primary}`,
      'background-color: #FFCC00': `background-color: ${siteConfig.colors.primary}`,
      'color: #FFCC00': `color: ${siteConfig.colors.primary}`,
      
      // Dark colors
      'background: #1E2024': `background: ${siteConfig.colors.dark}`,
      'bg-dark': 'bg-dark', // Keep class names as is
    };

    log('yellow', `  → Replacing content in files...`);
    replaceInFiles(targetFolder, replacements);

    log('green', `  ✓ Successfully created: ${siteConfig.folderName}`);
    return true;
  } catch (error) {
    log('red', `  ✗ Error: ${error.message}`);
    return false;
  }
}

/**
 * Main execution
 */
let successCount = 0;
let errorCount = 0;

config.sites.forEach((site, index) => {
  if (generateSite(site, index + 1)) {
    successCount++;
  } else {
    errorCount++;
  }
});

// Summary
log('blue', `\n${'='.repeat(60)}`);
log('cyan', '📊 GENERATION SUMMARY');
log('blue', `${'='.repeat(60)}`);
log('green', `✓ Success: ${successCount}/${config.sites.length}`);
if (errorCount > 0) {
  log('red', `✗ Failed: ${errorCount}/${config.sites.length}`);
}
log('blue', `${'='.repeat(60)}\n`);

if (successCount === config.sites.length) {
  log('green', '🎉 All sites generated successfully!');
  log('cyan', `\n📁 Folder Created:`);
  config.sites.forEach((site) => {
    log('cyan', `   ${path.join(baseDir, site.folderName)}`);
  });
  log('cyan', '\n📝 Next Steps:');
  log('cyan', '   1. Edit sites-config.json dengan nama portal dan warna yang sesuai');
  log('cyan', '   2. Jalankan script ini lagi: node tools/generate-sites.js');
  log('cyan', '   3. Setiap folder akan berisi website portal berita dengan tema custom\n');
  process.exit(0);
} else {
  log('red', '\n⚠ Some sites failed to generate. Check errors above.\n');
  process.exit(1);
}
