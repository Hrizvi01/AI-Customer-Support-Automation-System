import { useEffect, useRef } from "react";

export function useDialog(onClose, disabled) {
  const root = useRef(null);
  const options = useRef({ onClose, disabled });
  options.current = { onClose, disabled };
  useEffect(() => {
    const previous = document.activeElement;
    const focusable = () =>
      Array.from(
        root.current?.querySelectorAll(
          'button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), a[href], [tabindex="0"]',
        ) || [],
      ).filter((element) => element.offsetParent !== null);
    focusable()[0]?.focus({ preventScroll: true });
    function handleKey(event) {
      if (event.key === "Escape" && !options.current.disabled)
        options.current.onClose();
      if (event.key !== "Tab") return;
      const items = focusable();
      const first = items[0],
        last = items[items.length - 1];
      if (!first) {
        event.preventDefault();
        return;
      }
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }
    document.addEventListener("keydown", handleKey);
    return () => {
      document.removeEventListener("keydown", handleKey);
      previous?.focus({ preventScroll: true });
    };
  }, []);
  return root;
}
