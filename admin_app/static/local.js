document.addEventListener("DOMContentLoaded", () => {
  if (window.lucide) window.lucide.createIcons();

  const selectAll = document.querySelector("[data-select-all]");
  if (selectAll) {
    selectAll.addEventListener("change", () => {
      document.querySelectorAll('input[name="video_id"]').forEach((input) => {
        input.checked = selectAll.checked;
      });
    });
  }

  const active = Number(document.body.dataset.activeJobs || "0");
  const latest = document.body.dataset.latestJob || "";
  if (active > 0) {
    const poll = async () => {
      try {
        const response = await fetch("/api/state", { credentials: "same-origin" });
        if (!response.ok) return;
        const state = await response.json();
        if (state.active_jobs === 0 || String(state.latest_job_id || "") !== latest) {
          window.location.reload();
          return;
        }
      } catch (_) {
        return;
      }
      window.setTimeout(poll, 2500);
    };
    window.setTimeout(poll, 1200);
  }
});
