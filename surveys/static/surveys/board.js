"use strict";

const addButton = document.querySelector("[data-add-survey]");
const addDialog = document.querySelector("#add-dialog");
const detailDialog = document.querySelector("#detail-dialog");
const detailContent = document.querySelector("#detail-content");
const grid = document.querySelector("#survey-grid");
const emptyState = document.querySelector("#empty-state");
const count = document.querySelector("#survey-count");
const boardUrl = document.querySelector(".brand").href;

let detailRequest;
let expiryTimer;

function isPlainClick(event) {
    return event.button === 0 && !event.metaKey && !event.ctrlKey &&
        !event.shiftKey && !event.altKey;
}

function showDetailMessage(name) {
    const template = document.querySelector("#detail-" + name);
    detailContent.replaceChildren(template.content.cloneNode(true));
}

function syncCanvas() {
    const remaining = grid.children.length;
    count.textContent = remaining;
    count.setAttribute("aria-label", remaining + " survei aktif");
    grid.hidden = remaining === 0;
    emptyState.hidden = remaining > 0;
}

function refreshExpiry() {
    window.clearTimeout(expiryTimer);
    const now = Date.now();
    let nextExpiry = Infinity;

    for (const card of Array.from(grid.children)) {
        const expiry = Date.parse(card.dataset.expiresAt);
        if (expiry <= now) {
            card.remove();
        } else {
            nextExpiry = Math.min(nextExpiry, expiry);
        }
    }

    const detail = detailContent.querySelector("[data-detail-expires-at]");
    if (detail) {
        const expiry = Date.parse(detail.dataset.detailExpiresAt);
        if (expiry <= now) {
            showDetailMessage("expired");
        } else {
            nextExpiry = Math.min(nextExpiry, expiry);
        }
    }

    syncCanvas();
    if (Number.isFinite(nextExpiry)) {
        expiryTimer = window.setTimeout(refreshExpiry, nextExpiry - now + 50);
    }
}

function closeDialog(dialog) {
    if (dialog.hasAttribute("data-initial")) {
        window.location.assign(boardUrl);
        return;
    }
    dialog.close();
}

async function openDetail(cardLink) {
    detailRequest?.abort();
    const request = new AbortController();
    detailRequest = request;
    showDetailMessage("loading");
    detailDialog.showModal();

    try {
        const response = await fetch(cardLink.href, {
            headers: { "X-Survey-Fragment": "detail" },
            signal: request.signal,
        });

        if (request.signal.aborted) {
            return;
        }
        if (response.status === 404) {
            cardLink.closest("li").remove();
            showDetailMessage("expired");
            refreshExpiry();
            return;
        }
        if (!response.ok) {
            throw new Error("Gagal memuat ringkasan");
        }

        // HTML dirender dan di-escape di template Django dari origin yang sama.
        const html = await response.text();
        if (request.signal.aborted) {
            return;
        }
        detailContent.innerHTML = html;
        refreshExpiry();
    } catch (error) {
        if (!request.signal.aborted) {
            showDetailMessage("error");
        }
    }
}

if (typeof addDialog.showModal === "function") {
    addButton.addEventListener("click", (event) => {
        if (!isPlainClick(event)) {
            return;
        }
        event.preventDefault();
        addDialog.showModal();
    });

    grid.addEventListener("click", (event) => {
        const cardLink = event.target.closest("[data-survey-card]");
        if (!cardLink || !isPlainClick(event)) {
            return;
        }
        event.preventDefault();
        openDetail(cardLink);
    });

    for (const dialog of [addDialog, detailDialog]) {
        if (dialog.hasAttribute("data-initial")) {
            dialog.removeAttribute("open");
            dialog.showModal();
            dialog.querySelector('[aria-invalid="true"]')?.focus();
        }

        dialog.addEventListener("click", (event) => {
            const closeLink = event.target.closest("[data-close-dialog]");
            if (event.target === dialog || (closeLink && isPlainClick(event))) {
                event.preventDefault();
                closeDialog(dialog);
            }
        });

        dialog.addEventListener("cancel", (event) => {
            event.preventDefault();
            closeDialog(dialog);
        });
    }

    detailDialog.addEventListener("close", () => {
        detailRequest?.abort();
        detailContent.replaceChildren();
        refreshExpiry();
    });
}

window.addEventListener("pageshow", refreshExpiry);
refreshExpiry();
