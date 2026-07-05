(function () {
    var storageKey = "{{ project_name | lower }}-theme";
    var toggle = document.getElementById("theme-toggle");

    function setTheme(theme) {
        document.documentElement.dataset.theme = theme;
        localStorage.setItem(storageKey, theme);
    }

    if (toggle) {
        toggle.addEventListener("click", function () {
            var current = document.documentElement.dataset.theme || "light";
            setTheme(current === "dark" ? "light" : "dark");
        });
    }

    fetch("/api/about")
        .then(function (response) {
            return response.ok ? response.json() : null;
        })
        .then(function (payload) {
            if (payload) {
                console.info("{{ APP_NAME }} starter", payload);
            }
        })
        .catch(function () {
            console.info("{{ APP_NAME }} starter loaded for {{ project_name }}");
        });
}());
