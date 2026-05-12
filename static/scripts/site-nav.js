(() => {
  const nav = document.querySelector("[data-site-nav]");

  if (!nav) {
    return;
  }

  const rootPath = nav.dataset.rootPath || "";
  const links = [
    { label: "Home", href: "index.html" },
    { label: "Memos", href: "memos/index.html" },
    { label: "SOPs", href: "sops/index.html" },
    { label: "ESR Class", href: "content/esr-class/esr/main/sl1-esr-key.html" },
  ];

  const normalizePath = (href) => {
    const path = new URL(href, window.location.href).pathname;
    return path.replace(/\/index\.html$/, "/");
  };

  const currentPath = normalizePath(window.location.href);
  const list = document.createElement("ul");

  links.forEach(({ label, href }) => {
    const resolvedHref = `${rootPath}${href}`;

    if (normalizePath(resolvedHref) === currentPath) {
      return;
    }

    const item = document.createElement("li");
    const link = document.createElement("a");
    link.href = resolvedHref;
    link.textContent = label;
    item.appendChild(link);
    list.appendChild(item);
  });

  nav.appendChild(list);
})();
