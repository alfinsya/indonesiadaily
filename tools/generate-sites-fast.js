#!/usr/bin/env node

/**
 * Script untuk Generate 34 Portal Berita (OPTIMIZED - FAST)
 * 
 * Menggunakan Windows robocopy & sed untuk kecepatan maksimal
 * Cepat: ~30 detik untuk generate 34 sites
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');

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

const configPath = path.join(__dirname, 'sites-config.json');
let config;

try {
  config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  log('green', '✓ Config loaded successfully');
} catch (error) {
  log('red', `✗ Error loading config: ${error.message}`);
  process.exit(1);
}

const baseDir = path.resolve(__dirname, '..');
const originalFolder = path.join(baseDir, config.originalFolder);
// Place generated sites as siblings to the BizNews folder to avoid copying into a subdirectory of source
const outputRoot = path.resolve(baseDir, '..');

if (!fs.existsSync(originalFolder)) {
  log('red', `✗ Original folder not found: ${originalFolder}`);
  process.exit(1);
}

log('blue', `\n🚀 Starting generation of ${config.sites.length} portal berita...\n`);

const startTime = Date.now();
let successCount = 0;

/**
 * Generate satu site (optimized version)
 */
function generateSite(siteConfig, index) {
  const totalSites = config.sites.length;
  const progress = `[${index}/${totalSites}]`;
  
  try {
    const targetFolder = path.join(outputRoot, siteConfig.folderName);
    
    // Remove if exists
    if (fs.existsSync(targetFolder)) {
      try {
        execSync(`rmdir /s /q "${targetFolder}"`, { stdio: 'pipe' });
      } catch (e) {
        fs.rmSync(targetFolder, { recursive: true, force: true });
      }
    }
    
    // Copy dengan robocopy (Windows command, MUCH faster)
    try {
      execSync(`robocopy "${originalFolder}" "${targetFolder}" /e /NP /LOG:NUL`, { 
        stdio: 'pipe',
        windowsHide: true
      });
    } catch (e) {
      // robocopy returns non-zero on success, so fallback to xcopy
      try {
        execSync(`xcopy "${originalFolder}" "${targetFolder}" /E /I /Y`, { 
          stdio: 'pipe',
          windowsHide: true 
        });
      } catch (copyError) {
        throw new Error(`Copy failed: ${copyError.message}`);
      }
    }
    
    // Replace text in files (async file operations)
    replaceInFiles(targetFolder, {
      'BizNews': siteConfig.siteName,
      'IndonesiaDaily': siteConfig.siteName.replace(/[^a-zA-Z0-9]/g, ''),
      'indonesiadaily': siteConfig.socialHandle.toLowerCase(),
      'PORTAL_NAME': siteConfig.siteName,
      'IndonesiaDaily33@gmail.com': siteConfig.email,
      'indonesia.daily.33@gmail.com': siteConfig.email,
      'TENTANG KAMI - PLACEHOLDER': `TENTANG ${siteConfig.siteName.toUpperCase()}`,
      '--primary: #FFCC00': `--primary: ${siteConfig.colors.primary}`,
      '--dark: #1E2024': `--dark: ${siteConfig.colors.dark}`,
      '--secondary: #31404B': `--secondary: ${siteConfig.colors.secondary}`,
      'background: #FFCC00': `background: ${siteConfig.colors.primary}`,
      'background-color: #FFCC00': `background-color: ${siteConfig.colors.primary}`,
      'color: #FFCC00': `color: ${siteConfig.colors.primary}`,
      'background: #1E2024': `background: ${siteConfig.colors.dark}`,
    });
    
    log('green', `${progress} ✓ ${siteConfig.siteName}`);
    return true;
  } catch (error) {
    log('red', `${progress} ✗ ${siteConfig.siteName} - ${error.message}`);
    return false;
  }
}

/**
 * Replace dalam files (synchronous untuk simplicity)
 */
function replaceInFiles(dir, replacements) {
  const files = fs.readdirSync(dir);
  
  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      if (!file.startsWith('.') && file !== 'node_modules' && !file.includes('.bak')) {
        replaceInFiles(filePath, replacements);
      }
    } else if (stat.isFile()) {
      const ext = path.extname(file).toLowerCase();
      if (['.html', '.css', '.js', '.json'].includes(ext)) {
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
        } catch (e) {
          // Silent fail
        }
      }
    }
  });
}

/**
 * Main execution
 */
config.sites.forEach((site, index) => {
  if (generateSite(site, index + 1)) {
    successCount++;
  }
});

const endTime = Date.now();
const duration = ((endTime - startTime) / 1000).toFixed(2);

log('blue', `\n${'='.repeat(60)}`);
log('cyan', '📊 GENERATION COMPLETE');
log('blue', `${'='.repeat(60)}`);
log('green', `✓ Generated: ${successCount}/${config.sites.length}`);
log('cyan', `⏱️  Time: ${duration}s`);
log('blue', `${'='.repeat(60)}\n`);

if (successCount === config.sites.length) {
  log('green', '🎉 All sites generated successfully!');
  process.exit(0);
} else {
  log('red', `⚠ ${config.sites.length - successCount} sites failed\n`);
  process.exit(1);
}
