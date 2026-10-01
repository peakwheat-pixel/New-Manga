/**
 * Minimal DOM simulation for react-dom/client createRoot in vitest
 * (no jsdom/testing-library dependency — follows the inline MockElement
 * pattern first established by LibraryPanel.test.tsx, extracted here so
 * additional component suites can mount without duplicating ~120 lines).
 *
 * Supports exactly what the mounted-component tests need: an attachable
 * container with textContent aggregation and the node bookkeeping React's
 * initial mount performs. Event dispatch is NOT simulated — interaction
 * coverage lives at the client layer (invoke-parameter assertions).
 */

class MockNode {
  childNodes: MockNode[] = [];
  parentNode: MockNode | null = null;
  nodeType = 1;
  appendChild<T extends MockNode>(child: T): T {
    child.parentNode = this;
    this.childNodes.push(child);
    return child;
  }
  removeChild<T extends MockNode>(child: T): T {
    const idx = this.childNodes.indexOf(child);
    if (idx !== -1) {
      this.childNodes.splice(idx, 1);
      child.parentNode = null;
    }
    return child;
  }
  insertBefore<T extends MockNode>(newNode: T, refNode: MockNode | null): T {
    if (!refNode) return this.appendChild(newNode);
    const idx = this.childNodes.indexOf(refNode);
    if (idx !== -1) {
      newNode.parentNode = this;
      this.childNodes.splice(idx, 0, newNode);
    } else {
      this.appendChild(newNode);
    }
    return newNode;
  }
}

class MockElement extends MockNode {
  nodeName: string;
  tagName: string;
  attributes: Record<string, string> = {};
  style: Record<string, unknown> = {};
  ownerDocument: MockDocument;

  constructor(tag: string, ownerDoc: MockDocument) {
    super();
    this.nodeType = 1;
    this.nodeName = tag.toUpperCase();
    this.tagName = tag.toUpperCase();
    this.ownerDocument = ownerDoc;
  }
  setAttribute(k: string, v: unknown) {
    this.attributes[k] = String(v);
  }
  removeAttribute(k: string) {
    delete this.attributes[k];
  }
  getAttribute(k: string) {
    return this.attributes[k];
  }
  addEventListener() {}
  removeEventListener() {}
  // SELECT surface needed by react-dom's postMountWrapper → updateOptions:
  // it iterates `node.options`, reads each option's `value`, and assigns
  // `selected`. Event dispatch is NOT simulated.
  get options(): MockElement[] {
    return this.childNodes.filter(
      (c): c is MockElement => c instanceof MockElement && c.tagName === "OPTION",
    );
  }
  get value(): string {
    return this.attributes.value ?? this.textContent;
  }
  set value(v: string) {
    this.setAttribute("value", v);
  }
  get textContent(): string {
    return this.childNodes
      .map((c) => (c as unknown as MockElement | MockTextNode).textContent ?? "")
      .join("");
  }
  set textContent(v: string) {
    this.childNodes = [new MockTextNode(v, this.ownerDocument)];
  }
}

class MockHTMLIFrameElement extends MockElement {}

class MockTextNode extends MockNode {
  nodeName = "#text";
  nodeValue: string;
  ownerDocument: MockDocument;

  constructor(text: unknown, ownerDoc: MockDocument) {
    super();
    this.nodeType = 3;
    this.nodeValue = String(text);
    this.ownerDocument = ownerDoc;
  }
  get textContent(): string {
    return this.nodeValue;
  }
  set textContent(v: string) {
    this.nodeValue = v;
  }
}

export class MockDocument {
  nodeType = 9;
  nodeName = "#document";
  activeElement: MockElement | null = null;
  addEventListener: () => void = () => {};
  removeEventListener: () => void = () => {};

  createElement(tag: string): MockElement {
    return new MockElement(tag, this);
  }
  createTextNode(text: unknown): MockTextNode {
    return new MockTextNode(text, this);
  }
}

/** Build a (window, document) pair sufficient for createRoot mount tests. */
export function installMockDom(): { win: Record<string, unknown>; doc: MockDocument } {
  const doc = new MockDocument();
  const win: Record<string, unknown> = {
    addEventListener: () => {},
    removeEventListener: () => {},
    document: doc,
    Node: MockNode,
    Element: MockElement,
    HTMLIFrameElement: MockHTMLIFrameElement,
  };
  const globalAny = globalThis as unknown as Record<string, unknown>;
  globalAny.window = win;
  globalAny.document = doc;
  globalAny.Node = MockNode;
  globalAny.Element = MockElement;
  return { win, doc };
}
