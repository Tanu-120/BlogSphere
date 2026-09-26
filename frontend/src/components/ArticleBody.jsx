import Highlight from "./Highlight";

const MARK = /(\*\*[^*]+\*\*|\*[^*\n]+\*|_[^_\n]+_|`[^`]+`|\[[^\]]+\]\(https?:\/\/[^)\s]+\))/g;

function inline(text, keyPrefix, query) {
  const parts = String(text || "").split(MARK);
  return parts.map((part, index) => {
    const key = `${keyPrefix}-${index}`;
    if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
      return <strong key={key}>{inline(part.slice(2, -2), key, query)}</strong>;
    }
    if ((part.startsWith("*") && part.endsWith("*") && part.length > 2) || (part.startsWith("_") && part.endsWith("_") && part.length > 2)) {
      return <em key={key}>{inline(part.slice(1, -1), key, query)}</em>;
    }
    if (part.startsWith("`") && part.endsWith("`") && part.length > 2) {
      return <code key={key}>{part.slice(1, -1)}</code>;
    }
    const link = part.match(/^\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)$/);
    if (link) {
      return (
        <a key={key} href={link[2]} target="_blank" rel="noreferrer">
          {inline(link[1], key, query)}
        </a>
      );
    }
    return <Highlight key={key} text={part} query={query} />;
  });
}

function blocksFrom(text) {
  const lines = String(text || "").replace(/\r\n/g, "\n").split("\n");
  const blocks = [];
  let index = 0;

  while (index < lines.length) {
    const line = lines[index].trimEnd();
    if (!line.trim()) {
      index += 1;
      continue;
    }
    if (line.startsWith("### ")) {
      blocks.push({ type: "h3", text: line.slice(4).trim() });
      index += 1;
      continue;
    }
    if (line.startsWith("## ") || line.startsWith("# ")) {
      blocks.push({ type: "h2", text: line.slice(line.startsWith("## ") ? 3 : 2).trim() });
      index += 1;
      continue;
    }
    if (line.startsWith("> ")) {
      const quote = [];
      while (index < lines.length && lines[index].trimEnd().startsWith("> ")) {
        quote.push(lines[index].trimEnd().slice(2));
        index += 1;
      }
      blocks.push({ type: "quote", text: quote.join(" ") });
      continue;
    }
    if (line.startsWith("- ")) {
      const items = [];
      while (index < lines.length && lines[index].trimEnd().startsWith("- ")) {
        items.push(lines[index].trimEnd().slice(2));
        index += 1;
      }
      blocks.push({ type: "ul", items });
      continue;
    }
    if (/^\d+\.\s/.test(line)) {
      const items = [];
      while (index < lines.length && /^\d+\.\s/.test(lines[index].trimEnd())) {
        items.push(lines[index].trimEnd().replace(/^\d+\.\s/, ""));
        index += 1;
      }
      blocks.push({ type: "ol", items });
      continue;
    }
    blocks.push({ type: "p", text: line.trim() });
    index += 1;
  }
  return blocks;
}

export default function ArticleBody({ text, query = "" }) {
  const blocks = blocksFrom(text);

  return (
    <div className="article__body">
      {blocks.map((block, index) => {
        if (block.type === "h2") return <h2 key={index}>{inline(block.text, index, query)}</h2>;
        if (block.type === "h3") return <h3 key={index}>{inline(block.text, index, query)}</h3>;
        if (block.type === "quote") return <blockquote key={index}>{inline(block.text, index, query)}</blockquote>;
        if (block.type === "ul" || block.type === "ol") {
          const List = block.type === "ol" ? "ol" : "ul";
          return (
            <List key={index}>
              {block.items.map((item, itemIndex) => (
                <li key={itemIndex}>{inline(item, `${index}-${itemIndex}`, query)}</li>
              ))}
            </List>
          );
        }
        return <p key={index}>{inline(block.text, index, query)}</p>;
      })}
    </div>
  );
}
