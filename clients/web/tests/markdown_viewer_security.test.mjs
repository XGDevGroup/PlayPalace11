import assert from "node:assert/strict";
import test from "node:test";
import { renderMarkdownHtml } from "../ui/markdown_viewer.js";

const fakeMarked = {
  parse(markdown) {
    return String(markdown)
      .replace("SCRIPT", "<script>alert(1)</script>")
      .replace("IMG", '<img src="https://tracker.example/pixel.png">')
      .replace("AUDIO", '<audio src="https://tracker.example/audio.mp3"></audio>')
      .replace("VIDEO", '<video controls src="https://tracker.example/video.mp4"></video>')
      .replace("SOURCE", '<source src="https://tracker.example/video.mp4">')
      .replace("BUTTON", "<button>click me</button>")
      .replace("TEXTAREA", "<textarea>hidden</textarea>")
      .replace("SELECT", '<select><option>one</option><optgroup label="g"><option>two</option></optgroup></select>')
      .replace("DETAILS", "<details><summary>open</summary>body</details>")
      .replace("DIALOG", "<dialog open>modal</dialog>")
      .replace("FIELDSET", '<fieldset><label>Name</label><input value="x"></fieldset>')
      .replace("BACKGROUND", '<table background="https://tracker.example/bg.png"><tr><td>x</td></tr></table>')
      .replace("JSURL", '<a href="javascript:alert(1)">bad</a>')
      .replace("OKURL", '<a href="https://example.com">ok</a>');
  },
};

const fakePurifier = {
  sanitize(html, config) {
    const expectedForbiddenAttrs = ["style", "srcset", "background"];
    const expectedForbiddenTags = [
      "img",
      "svg",
      "math",
      "iframe",
      "object",
      "embed",
      "form",
      "style",
      "audio",
      "video",
      "source",
      "track",
      "picture",
      "input",
      "button",
      "link",
      "meta",
      "textarea",
      "select",
      "option",
      "optgroup",
      "details",
      "summary",
      "dialog",
      "fieldset",
      "label",
      "datalist",
      "legend",
      "output",
    ];

    assert.deepEqual(config?.USE_PROFILES, { html: true });
    assert.equal(config?.ALLOWED_URI_REGEXP?.test("https://example.com"), true);
    assert.equal(config?.ALLOWED_URI_REGEXP?.test("mailto:test@example.com"), true);
    assert.equal(config?.ALLOWED_URI_REGEXP?.test("javascript:alert(1)"), false);
    for (const attr of expectedForbiddenAttrs) {
      assert.equal(config?.FORBID_ATTR?.includes(attr), true, `missing forbidden attr ${attr}`);
    }
    for (const tag of expectedForbiddenTags) {
      assert.equal(config?.FORBID_TAGS?.includes(tag), true, `missing forbidden tag ${tag}`);
    }
    return html
      .replace(/<script[\s\S]*?<\/script>/gi, "")
      .replace(/<img[^>]*>/gi, "")
      .replace(/<audio[\s\S]*?<\/audio>/gi, "")
      .replace(/<video[\s\S]*?<\/video>/gi, "")
      .replace(/<source[^>]*>/gi, "")
      .replace(/<button[\s\S]*?<\/button>/gi, "")
      .replace(/<textarea[\s\S]*?<\/textarea>/gi, "")
      .replace(/<select[\s\S]*?<\/select>/gi, "")
      .replace(/<details[\s\S]*?<\/details>/gi, "")
      .replace(/<dialog[\s\S]*?<\/dialog>/gi, "")
      .replace(/<fieldset[\s\S]*?<\/fieldset>/gi, "")
      .replace(/\sbackground="[^"]*"/gi, "")
      .replace(/href="javascript:[^"]*"/gi, "");
  },
};

test("renderMarkdownHtml removes executable and remote-resource HTML", () => {
  const html = renderMarkdownHtml(
    "SCRIPT\nIMG\nAUDIO\nVIDEO\nSOURCE\nBUTTON\nTEXTAREA\nSELECT\nDETAILS\nDIALOG\nFIELDSET\nBACKGROUND\nJSURL\nOKURL",
    fakeMarked,
    fakePurifier,
  );

  assert.equal(html.includes("<script"), false);
  assert.equal(html.includes("<img"), false);
  assert.equal(html.includes("<audio"), false);
  assert.equal(html.includes("<video"), false);
  assert.equal(html.includes("<source"), false);
  assert.equal(html.includes("<button"), false);
  assert.equal(html.includes("<textarea"), false);
  assert.equal(html.includes("<select"), false);
  assert.equal(html.includes("<details"), false);
  assert.equal(html.includes("<dialog"), false);
  assert.equal(html.includes("<fieldset"), false);
  assert.equal(html.includes("tracker.example"), false);
  assert.equal(html.includes("background="), false);
  assert.equal(html.includes("javascript:"), false);
  assert.equal(html.includes("https://example.com"), true);
});

test("renderMarkdownHtml fallback escapes HTML metacharacters", () => {
  const html = renderMarkdownHtml("</pre><script>alert(1)</script>", null, null);

  assert.equal(html.includes("<script>"), false);
  assert.equal(html.includes("&lt;script&gt;"), true);
  assert.equal(html.includes("&lt;/pre&gt;"), true);
});
