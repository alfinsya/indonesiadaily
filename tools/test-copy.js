const fs = require('fs');
const path = require('path');

const baseDir = path.resolve(__dirname, '..');
const original = path.join(baseDir, '.'); // from config (BizNews folder)
// Place test target as sibling to avoid copying into a subdirectory of source
const outputRoot = path.resolve(baseDir, '..');
const target = path.join(outputRoot, 'site-test-copy');

console.log('Original folder:', original);
console.log('Target folder:', target);

try {
  if (fs.existsSync(target)) {
    console.log('Removing existing target...');
    fs.rmSync(target, { recursive: true, force: true });
  }
  console.log('Starting copy using fs.cpSync...');
  // Node 16+ supports fs.cpSync
  if (typeof fs.cpSync === 'function') {
    fs.cpSync(original, target, { recursive: true, errorOnExist: false });
    console.log('Copy completed successfully.');
  } else {
    console.log('fs.cpSync not available in this Node version. Falling back to manual copy (slow).');
    const copyRecursive = (src, dst) => {
      const stat = fs.statSync(src);
      if (stat.isDirectory()) {
        if (!fs.existsSync(dst)) fs.mkdirSync(dst);
        for (const item of fs.readdirSync(src)) {
          copyRecursive(path.join(src, item), path.join(dst, item));
        }
      } else {
        fs.copyFileSync(src, dst);
      }
    };
    copyRecursive(original, target);
    console.log('Fallback copy completed.');
  }
} catch (err) {
  console.error('Copy failed:', err && err.message ? err.message : err);
  console.error(err);
  process.exit(1);
}

process.exit(0);
