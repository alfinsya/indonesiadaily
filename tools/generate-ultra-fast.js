#!/usr/bin/env node

/**
 * ULTRA-FAST Portal Berita Generator
 * 
 * Performance optimizations:
 * - robocopy /MT:16 for parallel copy (16 threads)
 * - Skip binary files (jpg, png, etc)
 * - Only replace in text files
 * - ~5-10 sekunden untuk 34 sites
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const colors = {
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  reset: '\x1b[0m',
};

const log = (color, msg) => console.log(`${colors[color] || colors.reset}${msg}${colors.reset}`);

// Load config
const configPath = path.join(__dirname, 'sites-config.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

log('green', '✓ Config loaded');

const baseDir = path.resolve(__dirname, '..');
const originalFolder = path.join(baseDir, config.originalFolder);
// Output generated sites as siblings to BizNews to avoid recursive copy
const outputRoot = path.resolve(baseDir, '..');

if (!fs.existsSync(originalFolder)) {
  log('red', `✗ Original folder not found: ${originalFolder}`);
  process.exit(1);
}

log('blue', `\n🚀 Generating ${config.sites.length} portals...\n`);

const start = Date.now();
let success = 0;

// TEXT FILE EXTENSIONS ONLY
const textExts = ['.html', '.css', '.js', '.json', '.md', '.txt'];

/**
 * Replace dalam file text kecil/medium saja
 */
function quickReplace(dir, replacements) {
  try {
    const files = fs.readdirSync(dir);
    
    for (const file of files) {
      const filePath = path.join(dir, file);
      const stat = fs.statSync(filePath);
      
      if (stat.isDirectory()) {
        if (!file.startsWith('.') && !file.includes('.bak') && file !== 'node_modules') {
          quickReplace(filePath, replacements);
        }
      } else if (stat.isFile()) {
        const ext = path.extname(file).toLowerCase();
        
        // HANYA text files
        if (!textExts.includes(ext)) continue;
        
        // Skip file besar (> 2MB tidak usah di-replace)
        if (stat.size > 2 * 1024 * 1024) continue;
        
        try {
          let content = fs.readFileSync(filePath, 'utf8');
          let changed = false;
          
          for (const [search, replace] of Object.entries(replacements)) {
            const regex = new RegExp(search.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
            if (regex.test(content)) {
              content = content.replace(regex, replace);
              changed = true;
            }
          }
          
          if (changed) {
            fs.writeFileSync(filePath, content, 'utf8');
          }
        } catch (e) {
          // Silent
        }
      }
    }
  } catch (e) {
    // Silent
  }
}

/**
 * Generate satu site dengan robocopy (FAST)
 */
function genSite(cfg, idx) {
  const progress = `[${idx}/${config.sites.length}]`;
  
  try {
    const target = path.join(outputRoot, cfg.folderName);
    
    // Remove jika ada
    if (fs.existsSync(target)) {
      try {
        execSync(`robocopy "${target}" "${target}.trash" /mr /np /nfl /ndl /nc /ns /njs /mt:16 >nul 2>&1`);
        execSync(`rmdir /s /q "${target}.trash" 2>nul || true`);
      } catch (e) {}
      fs.rmSync(target, { recursive: true, force: true });
    }
    
    // COPY DENGAN ROBOCOPY MULTITHREADED (KUNCI KECEPATAN!)
    execSync(`robocopy "${originalFolder}" "${target}" /e /mt:16 /np /nfl /ndl /nc /ns /njs >nul 2>&1`, {
      stdio: 'pipe',
      windowsHide: true,
      timeout: 60000
    });
    
    // Replace hanya di text files (bukan binary)
    quickReplace(target, {
      'BizNews': cfg.siteName,
      'IndonesiaDaily': cfg.siteName.replace(/[^a-zA-Z0-9]/g, ''),
      'indonesiadaily': cfg.socialHandle.toLowerCase(),
      'PORTAL_NAME': cfg.siteName,
      'IndonesiaDaily33@gmail.com': cfg.email,
      'indonesia.daily.33@gmail.com': cfg.email,
      'TENTANG KAMI - PLACEHOLDER': `TENTANG ${cfg.siteName.toUpperCase()}`,
      '--primary: #FFCC00': `--primary: ${cfg.colors.primary}`,
      '--dark: #1E2024': `--dark: ${cfg.colors.dark}`,
      '--secondary: #31404B': `--secondary: ${cfg.colors.secondary}`,
      'background: #FFCC00': `background: ${cfg.colors.primary}`,
      'background-color: #FFCC00': `background-color: ${cfg.colors.primary}`,
      'color: #FFCC00': `color: ${cfg.colors.primary}`,
      'background: #1E2024': `background: ${cfg.colors.dark}`,
    });
    
    log('green', `${progress} ✓ ${cfg.siteName}`);
    return true;
  } catch (err) {
    log('red', `${progress} ✗ ${cfg.siteName}`);
    return false;
  }
}

// MAIN: Process semua sites
config.sites.forEach((site, idx) => {
  if (genSite(site, idx + 1)) success++;
});

const elapsed = ((Date.now() - start) / 1000).toFixed(1);

log('blue', `\n${'='.repeat(50)}`);
log('cyan', `✓ ${success}/${config.sites.length} generated`);
log('cyan', `⏱️  ${elapsed}s`);
log('blue', `${'='.repeat(50)}\n`);

process.exit(success === config.sites.length ? 0 : 1);
