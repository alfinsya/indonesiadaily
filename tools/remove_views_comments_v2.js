const fs = require('fs');
const path = require('path');

const articleDir = path.join(__dirname, '..', 'article');
const files = fs.readdirSync(articleDir).filter(f => f.endsWith('.html'));

let updated = 0;
files.forEach(file => {
  const filePath = path.join(articleDir, file);
  let content = fs.readFileSync(filePath, 'utf8');

  // Remove views span
  content = content.replace(/<span class="ml-3"><i class="far fa-eye mr-2"><\/i>\d+<\/span>/g, '');

  // Remove comments span
  content = content.replace(/<span class="ml-3"><i class="far fa-comment mr-2"><\/i>\d+<\/span>/g, '');

  // Remove comments section
  const commentsPattern = /<!-- Comment List Start -->[\s\S]*?<!-- Comment List End -->/g;
  content = content.replace(commentsPattern, '');

  fs.writeFileSync(filePath, content, 'utf8');
  updated++;
});

console.log('Updated ' + updated + ' article files');