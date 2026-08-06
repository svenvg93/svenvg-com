# Sven van Ginkel — Personal Blog

This is the source code for [svenvg.com](https://svenvg.com), a personal blog focused on self-hosting, networking, automation, and homelab infrastructure.

Built with [Hugo](https://gohugo.io) using the [hugo-narrow](https://github.com/tom2almighty/hugo-narrow) theme.

## ✨ Features

- Clean, responsive layout
- Markdown-based posts
- Support for drafts and scheduled content
- Syntax highlighting with line numbers
- Inline SVG diagrams per post

## 🚀 Local Development

```bash
# Clone the repo
git clone https://github.com/svenvg93/svenvg-com
cd svenvg-com

# Run the local server (includes drafts)
hugo server -D
```

## 🗂 Content Structure

Posts are located in `content/posts/YYYY-MM-DD-short-title/index.md` as page bundles.
Each post bundle can include:
- `index.md`: the post content
- any `.svg` diagrams referenced from the post body

## 🛠 Requirements

- [Hugo Extended](https://gohugo.io/getting-started/installing/) (v0.161.0+)

## 📄 License

This site’s content is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
