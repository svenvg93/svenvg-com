# Sven van Ginkel — Personal Blog

This is the source code for [svenvg.com](https://svenvg.com), a personal blog explaining how networking technologies and protocols work, plus the projects I build.

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

Create a new post with `hugo new posts/YYYY-MM-DD-short-title/index.md`.

Older step-by-step guides are parked in `unpublished/` (outside `content/`, so Hugo doesn't build them). To republish one, move its bundle back into `content/posts/` and give it one of the topic categories.

## 🛠 Requirements

- [Hugo Extended](https://gohugo.io/getting-started/installing/) (v0.161.0+)

## 📄 License

This site’s content is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
