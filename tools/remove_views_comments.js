const fs = require('fs');
const path = require('path');

const articleDir = path.join(__dirname, '..', 'article');
const files = fs.readdirSync(articleDir).filter(f => f.endsWith('.html'));

let updated = 0;
files.forEach(file => {
  const filePath = path.join(articleDir, file);
  let content = fs.readFileSync(filePath, 'utf8');

  // Remove views/comments section
  const viewsPattern = /<div class="d-flex justify-content-between bg-white border border-top-0 p-4">[\s\S]*?<\/div>/g;
  content = content.replace(viewsPattern, '');

  // Remove comments section
  const commentsPattern = /<!-- Comment List Start -->[\s\S]*?<!-- Comment List End -->/g;
  content = content.replace(commentsPattern, '');

  // Remove reporter/views/comments meta section
  const metaPattern = /<div class="d-flex mb-3">[\s\S]*?<\/div>/g;
  content = content.replace(metaPattern, '');
});

console.log('Updated ' + updated + ' article files');