// Dynamic year
document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("year").textContent = new Date().getFullYear();
});

document.addEventListener("DOMContentLoaded", async () => {
  const main = document.querySelector("main");

  try {
    const response = await fetch("WEBSITE_PROJECTS_LIST.json");
    const data = await response.json();

    // Alphabetical navigation
    const alphabetNav = document.createElement("nav");
    alphabetNav.className = "alphabet-nav";
    const letters = Object.keys(data);
    alphabetNav.innerHTML = letters
      .map((letter) => `<a href="#${letter}">${letter}</a>`)
      .join(" | ");
    main.appendChild(alphabetNav);

    // Projects sections
    letters.forEach((letter) => {
      const section = document.createElement("section");
      section.id = letter;

      const heading = document.createElement("h2");
      heading.textContent = letter;
      heading.className = "letter";
      section.appendChild(heading);

      data[letter].forEach((project) => {
        const card = document.createElement("div");
        card.className = "project-card";

        // Tittle
        const title = document.createElement("h3");
        title.className = "card-title";

        const link = document.createElement("a");
        link.href = project.github;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.className = "link";

        // GitHub icon
        const svgNS = "http://www.w3.org/2000/svg";
        const icon = document.createElementNS(svgNS, "svg");
        icon.setAttribute("viewBox", "0 0 512 512");
        icon.setAttribute("width", "20");
        icon.setAttribute("height", "20");
        icon.setAttribute("fill", "currentColor");
        icon.style.position = "relative";
        icon.style.top = "1px";
        icon.style.marginRight = "8px";

        const path = document.createElementNS(svgNS, "path");
        path.setAttribute(
          "d",
          "M173.9 397.4c0 2-2.3 3.6-5.2 3.6-3.3 .3-5.6-1.3-5.6-3.6 0-2 2.3-3.6 5.2-3.6 3-.3 5.6 1.3 5.6 3.6zm-31.1-4.5c-.7 2 1.3 4.3 4.3 4.9 2.6 1 5.6 0 6.2-2s-1.3-4.3-4.3-5.2c-2.6-.7-5.5 .3-6.2 2.3zm44.2-1.7c-2.9 .7-4.9 2.6-4.6 4.9 .3 2 2.9 3.3 5.9 2.6 2.9-.7 4.9-2.6 4.6-4.6-.3-1.9-3-3.2-5.9-2.9zM252.8 8c-138.7 0-244.8 105.3-244.8 244 0 110.9 69.8 205.8 169.5 239.2 12.8 2.3 17.3-5.6 17.3-12.1 0-6.2-.3-40.4-.3-61.4 0 0-70 15-84.7-29.8 0 0-11.4-29.1-27.8-36.6 0 0-22.9-15.7 1.6-15.4 0 0 24.9 2 38.6 25.8 21.9 38.6 58.6 27.5 72.9 20.9 2.3-16 8.8-27.1 16-33.7-55.9-6.2-112.3-14.3-112.3-110.5 0-27.5 7.6-41.3 23.6-58.9-2.6-6.5-11.1-33.3 2.6-67.9 20.9-6.5 69 27 69 27 20-5.6 41.5-8.5 62.8-8.5s42.8 2.9 62.8 8.5c0 0 48.1-33.6 69-27 13.7 34.7 5.2 61.4 2.6 67.9 16 17.7 25.8 31.5 25.8 58.9 0 96.5-58.9 104.2-114.8 110.5 9.2 7.9 17 22.9 17 46.4 0 33.7-.3 75.4-.3 83.6 0 6.5 4.6 14.4 17.3 12.1 100-33.2 167.8-128.1 167.8-239 0-138.7-112.5-244-251.2-244zM105.2 352.9c-1.3 1-1 3.3 .7 5.2 1.6 1.6 3.9 2.3 5.2 1 1.3-1 1-3.3-.7-5.2-1.6-1.6-3.9-2.3-5.2-1zm-10.8-8.1c-.7 1.3 .3 2.9 2.3 3.9 1.6 1 3.6 .7 4.3-.7 .7-1.3-.3-2.9-2.3-3.9-2-.6-3.6-.3-4.3 .7zm32.4 35.6c-1.6 1.3-1 4.3 1.3 6.2 2.3 2.3 5.2 2.6 6.5 1 1.3-1.3 .7-4.3-1.3-6.2-2.2-2.3-5.2-2.6-6.5-1zm-11.4-14.7c-1.6 1-1.6 3.6 0 5.9s4.3 3.3 5.6 2.3c1.6-1.3 1.6-3.9 0-6.2-1.4-2.3-4-3.3-5.6-2z"
        );
        icon.appendChild(path);
        link.appendChild(icon);
        link.appendChild(document.createTextNode(project.name));

        title.appendChild(link);
        card.appendChild(title);

        // Description
        if (project.description) {
          const desc = document.createElement("p");
          desc.innerHTML = project.description;
          desc.className = "description";
          card.appendChild(desc);
        }

        // Technology
        if (project.technology) {
          const tech = document.createElement("p");
          tech.innerHTML = `<strong>Technologies:</strong> ${project.technology}`;
          tech.className = "technology";
          card.appendChild(tech);
        }

        // Website link
        if (project.website) {
          const website = document.createElement("a");
          website.href = project.website;
          website.target = "_blank";
          website.rel = "noopener noreferrer";
          website.className = "website-link";

          // Add text
          const textNode = document.createTextNode("Website ");
          website.appendChild(textNode);

          // Add SVG icon
          const svgNS = "http://www.w3.org/2000/svg";
          const icon = document.createElementNS(svgNS, "svg");
          icon.setAttribute("viewBox", "0 0 640 640");
          icon.setAttribute("width", "18");
          icon.setAttribute("height", "18");
          icon.setAttribute("fill", "currentColor");
          icon.style.position = "relative";
          icon.style.top = "2px";
          icon.style.marginLeft = "4px";
          icon.innerHTML =
            '<path d="M384 64C366.3 64 352 78.3 352 96C352 113.7 366.3 128 384 128L466.7 128L265.3 329.4C252.8 341.9 252.8 362.2 265.3 374.7C277.8 387.2 298.1 387.2 310.6 374.7L512 173.3L512 256C512 273.7 526.3 288 544 288C561.7 288 576 273.7 576 256L576 96C576 78.3 561.7 64 544 64L384 64zM144 160C99.8 160 64 195.8 64 240L64 496C64 540.2 99.8 576 144 576L400 576C444.2 576 480 540.2 480 496L480 416C480 398.3 465.7 384 448 384C430.3 384 416 398.3 416 416L416 496C416 504.8 408.8 512 400 512L144 512C135.2 512 128 504.8 128 496L128 240C128 231.2 135.2 224 144 224L224 224C241.7 224 256 209.7 256 192C256 174.3 241.7 160 224 160L144 160z"/>';

          website.appendChild(icon);

          card.appendChild(website);
        }

        // Image
        if (project.image) {
          const img = document.createElement("img");
          img.src = project.image;
          img.alt = project.name;
          img.loading = "lazy";
          card.appendChild(img);
        }

        section.appendChild(card);
      });

      main.appendChild(section);
    });
  } catch (err) {
    console.error("Error loading projects:", err);
    main.textContent = "Failed to load projects.";
  }
});

// Go to Top button
const goTopBtn = document.getElementById("goTopBtn");

// Show button when scrolling down
window.onscroll = function () {
  if (
    document.body.scrollTop > 300 ||
    document.documentElement.scrollTop > 300
  ) {
    goTopBtn.style.display = "flex";
  } else {
    goTopBtn.style.display = "none";
  }
};

// Scroll to top when clicked
goTopBtn.addEventListener("click", () => {
  window.scrollTo({ top: 0, behavior: "smooth" });
});
