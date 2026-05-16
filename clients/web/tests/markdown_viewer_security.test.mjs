import assert from "node:assert/strict";
import test from "node:test";
import { renderMarkdownHtml } from "../ui/markdown_viewer.js";

const fakeMarked = {
  parse(markdown) {
    return String(markdown)
      .replace("SCRIPT", "<script>alert(1)</script>")
      .replace("IMG", '<img src="https://tracker.example/pixel.png">')
      .replace("JSURL", '<a href="javascript:alert(1)">bad</a>')
      .replace("OKURL", '<a href="https://example.com">ok</a>');
  },
};

const fakePurifier = {
  sanitize(html) {
    return html
      .replace(/<script[\s\S]*?<\/script>/gi, "")
      .replace(/<img[^>]*>/gi, "")
      .replace(/href="javascript:[^"]*"/gi, "");
  },
};

test("renderMarkdownHtml removes executable and remote-resource HTML", () => {
  const html = renderMarkdownHtml("SCRIPT\nIMG\nJSURL\nOKURL", fakeMarked, fakePurifier);

  assert.equal(html.includes("<script"), false);
  assert.equal(html.includes("<img"), false);
  assert.equal(html.includes("tracker.example"), false);
  assert.equal(html.includes("javascript:"), false);
  assert.equal(html.includes("https://example.com"), true);
});

test("renderMarkdownHtml fallback escapes HTML metacharacters", () => {
  const html = renderMarkdownHtml("</pre><script>alert(1)</script>", null, null);

  assert.equal(html.includes("<script>"), false);
  assert.equal(html.includes("&lt;script&gt;"), true);
  assert.equal(html.includes("&lt;/pre&gt;"), true);
});
