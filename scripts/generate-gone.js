const { execSync } = require("child_process");
const fs = require("fs");

const outputFile = "static/gone.json";

const deletedFiles = execSync(
  'git log --diff-filter=D --name-only --pretty=""'
)
  .toString()
  .split("\n")
  .filter(f => f.startsWith("content/") && f.endsWith(".md"))
  .filter(Boolean);

const gone = deletedFiles.map(file => {
  let slug = file
    .replace("content/", "")
    .replace(/\.md$/, "")
    .replace(/index$/, "");

  return "/" + slug + "/";
});

const uniqueGone = [...new Set(gone)];

fs.writeFileSync(
  outputFile,
  JSON.stringify({ gone: uniqueGone }, null, 2)
);

console.log("Generated gone.json:", uniqueGone);