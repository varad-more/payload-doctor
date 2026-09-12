import { forwardRef, useMemo, useRef } from "react";

interface EditorProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
}

export const Editor = forwardRef<HTMLTextAreaElement, EditorProps>(function Editor(
  { value, onChange, onSubmit },
  ref,
) {
  const gutterRef = useRef<HTMLPreElement>(null);
  const lineCount = useMemo(() => {
    let count = 1;
    for (const character of value) if (character === "\n") count += 1;
    return count;
  }, [value]);
  const lineNumbers = useMemo(
    () => (lineCount <= 3000 ? Array.from({ length: lineCount }, (_, index) => index + 1).join("\n") : "1\n⋮"),
    [lineCount],
  );

  return (
    <div className="editor-shell">
      <pre ref={gutterRef} className="line-gutter" aria-hidden="true">
        {lineNumbers}
      </pre>
      <textarea
        ref={ref}
        id="payload-content"
        className="payload-editor"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onScroll={(event) => {
          if (gutterRef.current) gutterRef.current.scrollTop = event.currentTarget.scrollTop;
        }}
        onKeyDown={(event) => {
          if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
            event.preventDefault();
            onSubmit();
          }
        }}
        aria-describedby="input-help"
        aria-label="JSON payload input"
        placeholder={'{\n  "paste": "your payload here"\n}'}
        spellCheck={false}
        wrap="off"
      />
    </div>
  );
});
