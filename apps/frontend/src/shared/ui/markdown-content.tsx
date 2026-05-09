import type { ReactNode } from "react";

type MarkdownContentProps = {
    content: string;
};

type Block =
    | { type: "paragraph"; content: string }
    | { type: "heading"; level: number; content: string }
    | { type: "unordered-list"; items: string[] }
    | { type: "ordered-list"; items: string[] }
    | { type: "blockquote"; items: string[] }
    | { type: "code"; language: string; content: string };

export function MarkdownContent({ content }: MarkdownContentProps) {
    const blocks = parseMarkdown(content);

    return (
        <div className="chat-markdown">
            {blocks.map((block, index) => renderBlock(block, index))}
        </div>
    );
}

function renderBlock(block: Block, index: number) {
    const key = `${block.type}-${index}`;

    if (block.type === "heading") {
        if (block.level === 1) {
            return <h1 key={key}>{renderInline(block.content)}</h1>;
        }

        if (block.level === 2) {
            return <h2 key={key}>{renderInline(block.content)}</h2>;
        }

        return <h3 key={key}>{renderInline(block.content)}</h3>;
    }

    if (block.type === "unordered-list") {
        return (
            <ul key={key}>
                {block.items.map((item, itemIndex) => (
                    <li key={`${key}-${itemIndex}`}>{renderInline(item)}</li>
                ))}
            </ul>
        );
    }

    if (block.type === "ordered-list") {
        return (
            <ol key={key}>
                {block.items.map((item, itemIndex) => (
                    <li key={`${key}-${itemIndex}`}>{renderInline(item)}</li>
                ))}
            </ol>
        );
    }

    if (block.type === "blockquote") {
        return (
            <blockquote key={key}>
                {block.items.map((item, itemIndex) => (
                    <p key={`${key}-${itemIndex}`}>{renderInline(item)}</p>
                ))}
            </blockquote>
        );
    }

    if (block.type === "code") {
        return (
            <pre key={key}>
                <code>{block.content}</code>
            </pre>
        );
    }

    return <p key={key}>{renderInline(block.content)}</p>;
}

function parseMarkdown(content: string): Block[] {
    const normalized = content.replace(/\r\n/g, "\n").trim();

    if (!normalized) {
        return [];
    }

    const lines = normalized.split("\n");
    const blocks: Block[] = [];
    let index = 0;

    while (index < lines.length) {
        const line = lines[index];
        const trimmed = line.trim();

        if (!trimmed) {
            index += 1;
            continue;
        }

        const codeFenceMatch = trimmed.match(/^```([a-zA-Z0-9_-]+)?$/);
        if (codeFenceMatch) {
            const language = codeFenceMatch[1] ?? "";
            index += 1;
            const codeLines: string[] = [];

            while (index < lines.length && !lines[index].trim().startsWith("```")) {
                codeLines.push(lines[index]);
                index += 1;
            }

            if (index < lines.length) {
                index += 1;
            }

            blocks.push({
                type: "code",
                language,
                content: codeLines.join("\n"),
            });
            continue;
        }

        const headingMatch = trimmed.match(/^(#{1,6})\s+(.+)$/);
        if (headingMatch) {
            blocks.push({
                type: "heading",
                level: Math.min(headingMatch[1].length, 3),
                content: headingMatch[2],
            });
            index += 1;
            continue;
        }

        if (/^[-*]\s+/.test(trimmed)) {
            const items: string[] = [];

            while (index < lines.length && /^[-*]\s+/.test(lines[index].trim())) {
                items.push(lines[index].trim().replace(/^[-*]\s+/, ""));
                index += 1;
            }

            blocks.push({ type: "unordered-list", items });
            continue;
        }

        if (/^\d+\.\s+/.test(trimmed)) {
            const items: string[] = [];

            while (index < lines.length && /^\d+\.\s+/.test(lines[index].trim())) {
                items.push(lines[index].trim().replace(/^\d+\.\s+/, ""));
                index += 1;
            }

            blocks.push({ type: "ordered-list", items });
            continue;
        }

        if (/^>\s+/.test(trimmed)) {
            const items: string[] = [];

            while (index < lines.length && /^>\s+/.test(lines[index].trim())) {
                items.push(lines[index].trim().replace(/^>\s+/, ""));
                index += 1;
            }

            blocks.push({ type: "blockquote", items });
            continue;
        }

        const paragraphLines: string[] = [];

        while (index < lines.length) {
            const currentLine = lines[index];
            const currentTrimmed = currentLine.trim();

            if (!currentTrimmed) {
                break;
            }

            if (
                currentTrimmed.startsWith("```") ||
                /^(#{1,6})\s+/.test(currentTrimmed) ||
                /^[-*]\s+/.test(currentTrimmed) ||
                /^\d+\.\s+/.test(currentTrimmed) ||
                /^>\s+/.test(currentTrimmed)
            ) {
                break;
            }

            paragraphLines.push(currentTrimmed);
            index += 1;
        }

        blocks.push({
            type: "paragraph",
            content: paragraphLines.join(" "),
        });
    }

    return blocks;
}

function renderInline(content: string): ReactNode[] {
    const nodes: ReactNode[] = [];
    const pattern = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[[^\]]+\]\([^)]+\))/g;
    let lastIndex = 0;
    let match: RegExpExecArray | null;

    match = pattern.exec(content);
    while (match) {
        const token = match[0];

        if (match.index > lastIndex) {
            nodes.push(content.slice(lastIndex, match.index));
        }

        if (token.startsWith("**") && token.endsWith("**")) {
            nodes.push(<strong key={`strong-${match.index}`}>{token.slice(2, -2)}</strong>);
        } else if (token.startsWith("*") && token.endsWith("*")) {
            nodes.push(<em key={`em-${match.index}`}>{token.slice(1, -1)}</em>);
        } else if (token.startsWith("`") && token.endsWith("`")) {
            nodes.push(<code key={`code-${match.index}`}>{token.slice(1, -1)}</code>);
        } else if (token.startsWith("[")) {
            const linkMatch = token.match(/^\[([^\]]+)\]\(([^)]+)\)$/);

            if (linkMatch) {
                nodes.push(
                    <a
                        key={`link-${match.index}`}
                        href={linkMatch[2]}
                        target="_blank"
                        rel="noreferrer"
                    >
                        {linkMatch[1]}
                    </a>,
                );
            } else {
                nodes.push(token);
            }
        }

        lastIndex = match.index + token.length;
        match = pattern.exec(content);
    }

    if (lastIndex < content.length) {
        nodes.push(content.slice(lastIndex));
    }

    return nodes;
}
