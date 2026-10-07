/**
 * PosterKart - Premium Interactions & AJAX JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavbarScroll();
    initSearchSuggestions();
    initWishlistToggles();
    initAddToCartForms();
    initCartDrawer();
    initQuickViewModal();
    initProductDetailInteractions();
    initCustomPosterStudio();
});

// ----------------------------------------------------
// Helper: Get CSRF Cookie
// ----------------------------------------------------
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// ----------------------------------------------------
// Toast Notification Engine
// ----------------------------------------------------
function showToast(message, type = 'default') {
    let container = document.getElementById('pkToastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'pkToastContainer';
        container.className = 'pk-toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'pk-toast';
    
    let icon = 'bi-check-circle-fill text-success';
    if (type === 'heart') icon = 'bi-heart-fill text-danger';
    if (type === 'error') icon = 'bi-exclamation-circle-fill text-danger';
    if (type === 'info') icon = 'bi-info-circle-fill text-info';

    toast.innerHTML = `
        <i class="bi ${icon} fs-5"></i>
        <div>${message}</div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// ----------------------------------------------------
// 1. Sticky Navbar
// ----------------------------------------------------
function initNavbarScroll() {
    const navbar = document.querySelector('.pk-navbar');
    if (!navbar) return;
    window.addEventListener('scroll', () => {
        if (window.scrollY > 30) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// ----------------------------------------------------
// 2. Debounced Live Search Suggestions
// ----------------------------------------------------
function initSearchSuggestions() {
    const searchInput = document.getElementById('globalSearchInput');
    const dropdown = document.getElementById('searchSuggestionsDropdown');
    if (!searchInput || !dropdown) return;

    let debounceTimer;

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        clearTimeout(debounceTimer);

        if (query.length < 2) {
            dropdown.style.display = 'none';
            dropdown.innerHTML = '';
            return;
        }

        debounceTimer = setTimeout(() => {
            fetch(`/api/search-suggestions/?q=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(data => {
                    if (data.suggestions && data.suggestions.length > 0) {
                        let html = '<div class="p-2 border-bottom text-muted small fw-bold">POSTER SUGGESTIONS</div>';
                        data.suggestions.forEach(item => {
                            html += `
                                <a href="${item.url}" class="d-flex align-items-center gap-3 p-2 border-bottom text-decoration-none text-dark search-item-hover">
                                    <img src="${item.image}" width="40" height="50" class="rounded object-fit-cover shadow-xs" alt="${item.title}">
                                    <div>
                                        <div class="fw-bold text-truncate" style="max-width: 200px;">${item.title}</div>
                                        <div class="text-muted small">${item.category} • <span class="text-danger fw-semibold">₹${item.price.toFixed(0)}</span></div>
                                    </div>
                                </a>
                            `;
                        });
                        html += `<div class="p-2 text-center bg-light"><a href="/shop/?q=${encodeURIComponent(query)}" class="small text-danger fw-bold">View all results for "${query}" →</a></div>`;
                        dropdown.innerHTML = html;
                        dropdown.style.display = 'block';
                    } else {
                        dropdown.innerHTML = `<div class="p-3 text-muted text-center small">No posters matching "<b>${query}</b>"</div>`;
                        dropdown.style.display = 'block';
                    }
                })
                .catch(err => console.error('Search error:', err));
        }, 250);
    });

    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });
}

// ----------------------------------------------------
// 3. Wishlist AJAX Toggle
// ----------------------------------------------------
function initWishlistToggles() {
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.btn-wishlist-toggle');
        if (!btn) return;
        e.preventDefault();

        const posterId = btn.dataset.posterId;
        if (!posterId) return;

        fetch(`/cart/wishlist/toggle/${posterId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(res => {
            if (res.status === 401) {
                return res.json().then(d => {
                    showToast(d.message, 'error');
                    setTimeout(() => window.location.href = d.login_url, 1200);
                    return null;
                });
            }
            return res.json();
        })
        .then(data => {
            if (!data) return;
            if (data.status === 'success') {
                const isAdded = data.action === 'added';
                // Update button visuals
                document.querySelectorAll(`.btn-wishlist-toggle[data-poster-id="${posterId}"]`).forEach(el => {
                    if (isAdded) {
                        el.classList.add('active');
                        el.innerHTML = '<i class="bi bi-heart-fill text-danger"></i>';
                    } else {
                        el.classList.remove('active');
                        el.innerHTML = '<i class="bi bi-heart"></i>';
                    }
                });

                // Update navbar wishlist count badge
                const badge = document.getElementById('navbarWishlistCount');
                if (badge) {
                    badge.innerText = data.wishlist_count;
                    badge.style.display = data.wishlist_count > 0 ? 'flex' : 'none';
                }

                showToast(data.message, 'heart');
            }
        })
        .catch(err => console.error('Wishlist error:', err));
    });
}

// ----------------------------------------------------
// 4. AJAX Add to Cart & Cart Drawer
// ----------------------------------------------------
function initAddToCartForms() {
    document.addEventListener('submit', (e) => {
        const form = e.target.closest('.ajax-add-to-cart-form');
        if (!form) return;
        
        const submitBtn = form.querySelector('button[type="submit"]');
        const isBuyNow = e.submitter && e.submitter.value === 'buy_now';
        if (isBuyNow) return; // Allow normal form submission for direct Buy Now checkout

        e.preventDefault();

        const formData = new FormData(form);
        formData.append('ajax', '1');

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Adding...';
        }

        fetch('/cart/add/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="bi bi-check2 me-1"></i> Added!';
                setTimeout(() => {
                    submitBtn.innerHTML = '<i class="bi bi-bag-plus me-1"></i> Add to Cart';
                }, 2000);
            }

            if (data.status === 'success') {
                updateCartBadges(data.cart_count);
                showToast(data.message, 'default');
                openCartDrawer();
                refreshCartDrawer();
            }
        })
        .catch(err => {
            console.error('Add to cart error:', err);
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="bi bi-bag-plus me-1"></i> Add to Cart';
            }
        });
    });

    // Quick Add button directly from cards
    document.addEventListener('click', (e) => {
        const quickBtn = e.target.closest('.btn-quick-add-cart');
        if (!quickBtn) return;
        e.preventDefault();

        const posterId = quickBtn.dataset.posterId;
        const formData = new FormData();
        formData.append('poster_id', posterId);
        formData.append('quantity', '1');
        formData.append('ajax', '1');

        fetch('/cart/add/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                updateCartBadges(data.cart_count);
                showToast(data.message, 'default');
                openCartDrawer();
                refreshCartDrawer();
            }
        })
        .catch(err => console.error('Quick add error:', err));
    });
}

function updateCartBadges(count) {
    document.querySelectorAll('.navbar-cart-count').forEach(el => {
        el.innerText = count;
        el.style.display = count > 0 ? 'flex' : 'none';
    });
}

// ----------------------------------------------------
// 5. Cart Drawer Management
// ----------------------------------------------------
function initCartDrawer() {
    const backdrop = document.getElementById('cartDrawerBackdrop');
    const drawer = document.getElementById('cartDrawer');
    const openBtns = document.querySelectorAll('.btn-open-cart-drawer');
    const closeBtn = document.getElementById('btnCloseCartDrawer');

    openBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            openCartDrawer();
            refreshCartDrawer();
        });
    });

    if (closeBtn) closeBtn.addEventListener('click', closeCartDrawer);
    if (backdrop) backdrop.addEventListener('click', closeCartDrawer);
}

function openCartDrawer() {
    const backdrop = document.getElementById('cartDrawerBackdrop');
    const drawer = document.getElementById('cartDrawer');
    if (backdrop && drawer) {
        backdrop.classList.add('active');
        drawer.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
}

function closeCartDrawer() {
    const backdrop = document.getElementById('cartDrawerBackdrop');
    const drawer = document.getElementById('cartDrawer');
    if (backdrop && drawer) {
        backdrop.classList.remove('active');
        drawer.classList.remove('active');
        document.body.style.overflow = '';
    }
}

function refreshCartDrawer() {
    const body = document.getElementById('cartDrawerItemsList');
    const subtotalEl = document.getElementById('cartDrawerSubtotal');
    const deliveryEl = document.getElementById('cartDrawerDelivery');
    const totalEl = document.getElementById('cartDrawerTotal');
    if (!body) return;

    fetch('/cart/drawer-json/')
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                updateCartBadges(data.cart_count);

                if (data.items.length === 0) {
                    body.innerHTML = `
                        <div class="text-center py-5">
                            <div class="fs-1 text-muted mb-2"><i class="bi bi-bag"></i></div>
                            <h6 class="fw-bold mb-1">Your cart is empty</h6>
                            <p class="text-muted small mb-4">Discover beautiful wall posters and transform your space.</p>
                            <a href="/shop/" class="btn btn-pk-dark btn-sm" onclick="closeCartDrawer()">Explore Shop</a>
                        </div>
                    `;
                    if (subtotalEl) subtotalEl.innerText = '₹0.00';
                    if (totalEl) totalEl.innerText = '₹0.00';
                    return;
                }

                let html = '';
                data.items.forEach(item => {
                    html += `
                        <div class="d-flex gap-3 pb-3 mb-3 border-bottom align-items-center">
                            <img src="${item.image_url}" width="60" height="80" class="rounded object-fit-cover shadow-xs" alt="${item.title}">
                            <div class="flex-grow-1">
                                <div class="fw-bold text-truncate" style="max-width: 220px;">${item.title}</div>
                                <div class="text-muted small">${item.size} • ${item.frame}</div>
                                <div class="d-flex align-items-center justify-content-between mt-2">
                                    <div class="d-flex align-items-center border rounded">
                                        <button type="button" class="btn btn-sm btn-link text-dark px-2 py-0 drawer-qty-btn" onclick="updateCartItemQty(${item.id}, 'decrease')">−</button>
                                        <span class="px-2 small fw-bold">${item.quantity}</span>
                                        <button type="button" class="btn btn-sm btn-link text-dark px-2 py-0 drawer-qty-btn" onclick="updateCartItemQty(${item.id}, 'increase')">+</button>
                                    </div>
                                    <div class="fw-bold text-dark">₹${item.total_price.toFixed(0)}</div>
                                </div>
                            </div>
                        </div>
                    `;
                });
                body.innerHTML = html;

                if (subtotalEl) subtotalEl.innerText = `₹${data.subtotal.toFixed(0)}`;
                if (deliveryEl) deliveryEl.innerText = data.delivery_charge === 0 ? 'FREE' : `₹${data.delivery_charge.toFixed(0)}`;
                if (totalEl) totalEl.innerText = `₹${data.total_amount.toFixed(0)}`;
            }
        })
        .catch(err => console.error('Cart drawer fetch error:', err));
}

window.updateCartItemQty = function(itemId, action) {
    fetch(`/cart/update/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `action=${action}`
    })
    .then(res => res.json())
    .then(data => {
        refreshCartDrawer();
        // If on the full cart page, reload or update DOM
        if (window.location.pathname.includes('/cart/')) {
            window.location.reload();
        }
    });
};

// ----------------------------------------------------
// 6. Quick View Modal
// ----------------------------------------------------
function initQuickViewModal() {
    const modalEl = document.getElementById('quickViewModal');
    if (!modalEl) return;

    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.btn-quick-view');
        if (!btn) return;

        const slug = btn.dataset.slug;
        if (!slug) return;

        fetch(`/api/quick-view/${slug}/`)
            .then(res => res.json())
            .then(resData => {
                if (resData.status === 'success') {
                    const p = resData.data;
                    document.getElementById('qvTitle').innerText = p.title;
                    document.getElementById('qvCategory').innerText = p.category;
                    document.getElementById('qvDescription').innerText = p.description;
                    document.getElementById('qvImage').src = p.main_image;
                    document.getElementById('qvDetailLink').href = p.detail_url;
                    document.getElementById('qvPosterId').value = p.id;
                    document.getElementById('qvRating').innerHTML = `★ ${p.rating} (${p.review_count} reviews)`;
                    
                    // Render size options
                    let sizeHtml = '';
                    p.sizes.forEach((s, idx) => {
                        const checked = s.is_default || idx === 0 ? 'checked' : '';
                        sizeHtml += `
                            <div>
                                <input type="radio" name="size_id" value="${s.id}" data-extra="${s.extra_price}" id="qv_size_${s.id}" class="option-card-radio qv-size-radio" ${checked}>
                                <label for="qv_size_${s.id}" class="option-card-label py-2">
                                    <div class="option-title small">${s.code}</div>
                                    <div class="option-price">${s.extra_price > 0 ? '+₹' + s.extra_price.toFixed(0) : 'Base'}</div>
                                </label>
                            </div>
                        `;
                    });
                    document.getElementById('qvSizeGrid').innerHTML = sizeHtml;

                    // Render frame options
                    let frameHtml = '';
                    p.frames.forEach((f, idx) => {
                        const checked = f.is_default || idx === 0 ? 'checked' : '';
                        frameHtml += `
                            <div>
                                <input type="radio" name="frame_id" value="${f.id}" data-extra="${f.extra_price}" id="qv_frame_${f.id}" class="option-card-radio qv-frame-radio" ${checked}>
                                <label for="qv_frame_${f.id}" class="option-card-label py-2">
                                    <div class="option-title small text-truncate">${f.name.split(' ')[0]}</div>
                                    <div class="option-price">${f.extra_price > 0 ? '+₹' + f.extra_price.toFixed(0) : 'Free'}</div>
                                </label>
                            </div>
                        `;
                    });
                    document.getElementById('qvFrameGrid').innerHTML = frameHtml;

                    // Price update calculation
                    const basePrice = p.base_price;
                    const updateQvPrice = () => {
                        const selSize = document.querySelector('.qv-size-radio:checked');
                        const selFrame = document.querySelector('.qv-frame-radio:checked');
                        const sizeExtra = selSize ? parseFloat(selSize.dataset.extra || 0) : 0;
                        const frameExtra = selFrame ? parseFloat(selFrame.dataset.extra || 0) : 0;
                        const finalPrice = basePrice + sizeExtra + frameExtra;
                        document.getElementById('qvPrice').innerText = `₹${finalPrice.toFixed(0)}`;
                    };

                    document.querySelectorAll('.qv-size-radio, .qv-frame-radio').forEach(r => {
                        r.addEventListener('change', updateQvPrice);
                    });
                    updateQvPrice();

                    const bsModal = new bootstrap.Modal(modalEl);
                    bsModal.show();
                }
            })
            .catch(err => console.error('Quick view error:', err));
    });
}

// ----------------------------------------------------
// 7. Product Detail Page Live Pricing & Mockup Switcher
// ----------------------------------------------------
function initProductDetailInteractions() {
    const detailForm = document.getElementById('productDetailForm');
    if (!detailForm) return;

    const basePrice = parseFloat(detailForm.dataset.basePrice || 299);
    const priceDisplay = document.getElementById('detailFinalPrice');
    const mockupFrame = document.getElementById('mockupPosterFrame');
    const mockupContainer = document.getElementById('mockupContainer');

    function calculateDetailPrice() {
        const selSize = detailForm.querySelector('input[name="size_id"]:checked');
        const selFrame = detailForm.querySelector('input[name="frame_id"]:checked');
        const qtyInput = detailForm.querySelector('input[name="quantity"]');
        const qty = qtyInput ? parseInt(qtyInput.value) || 1 : 1;

        const sizeExtra = selSize ? parseFloat(selSize.dataset.extraPrice || 0) : 0;
        const frameExtra = selFrame ? parseFloat(selFrame.dataset.extraPrice || 0) : 0;
        const frameType = selFrame ? selFrame.dataset.frameType : 'none';

        const unit = basePrice + sizeExtra + frameExtra;
        const total = unit * qty;

        if (priceDisplay) {
            priceDisplay.innerText = `₹${total.toFixed(0)}`;
        }

        // Update mockup frame style live!
        if (mockupFrame) {
            mockupFrame.className = `mockup-poster-frame frame-${frameType}`;
        }
    }

    detailForm.querySelectorAll('input[name="size_id"], input[name="frame_id"]').forEach(el => {
        el.addEventListener('change', calculateDetailPrice);
    });

    const qtyInput = detailForm.querySelector('input[name="quantity"]');
    if (qtyInput) {
        qtyInput.addEventListener('input', calculateDetailPrice);
    }

    // Room Switcher Tabs for Wall Mockup
    document.querySelectorAll('.btn-mockup-scene').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.btn-mockup-scene').forEach(b => b.classList.remove('active', 'btn-dark'));
            document.querySelectorAll('.btn-mockup-scene').forEach(b => b.classList.add('btn-outline-dark'));
            btn.classList.add('active', 'btn-dark');
            btn.classList.remove('btn-outline-dark');

            const scene = btn.dataset.scene;
            if (mockupContainer) {
                mockupContainer.className = `mockup-container ${scene}`;
            }
        });
    });

    // Gallery Thumbnail Switcher
    document.querySelectorAll('.product-thumbnail-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const newSrc = btn.dataset.fullSrc;
            const mainImg = document.getElementById('mainProductImage');
            const mockupImg = document.getElementById('mockupPosterImage');
            if (mainImg && newSrc) mainImg.src = newSrc;
            if (mockupImg && newSrc) mockupImg.src = newSrc;

            document.querySelectorAll('.product-thumbnail-btn').forEach(b => b.classList.remove('border-danger', 'border-2'));
            btn.classList.add('border-danger', 'border-2');
        });
    });

    calculateDetailPrice();
}

// ----------------------------------------------------
// 8. Custom Poster Studio Drag & Drop Live Preview
// ----------------------------------------------------
function initCustomPosterStudio() {
    const dropzone = document.getElementById('customPosterDropzone');
    const fileInput = document.getElementById('customPosterFileInput');
    const previewContainer = document.getElementById('customPreviewContainer');
    const previewImg = document.getElementById('customPreviewImage');
    const previewTextOverlay = document.getElementById('customPreviewTextOverlay');
    const textInput = document.getElementById('id_custom_text');
    const form = document.getElementById('customPosterStudioForm');

    if (!dropzone || !fileInput) return;

    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });
    ['dragleave', 'dragend'].forEach(type => {
        dropzone.addEventListener(type, () => dropzone.classList.remove('dragover'));
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            handleCustomFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleCustomFile(e.target.files[0]);
        }
    });

    function handleCustomFile(file) {
        if (!file.type.match('image.*')) {
            showToast('Please upload a valid JPG or PNG image.', 'error');
            return;
        }
        const reader = new FileReader();
        reader.onload = (e) => {
            if (previewImg) {
                previewImg.src = e.target.result;
            }
            if (previewContainer) {
                previewContainer.classList.remove('d-none');
            }
            dropzone.innerHTML = `
                <i class="bi bi-check-circle-fill text-success fs-1 mb-2"></i>
                <h6 class="fw-bold mb-1">${file.name}</h6>
                <p class="text-muted small mb-0">Click or drag another image to replace</p>
            `;
        };
        reader.readAsDataURL(file);
    }

    if (textInput && previewTextOverlay) {
        textInput.addEventListener('input', (e) => {
            previewTextOverlay.innerText = e.target.value;
        });
    }

    // Dynamic Price Calculation for Custom Poster Studio
    if (form) {
        const baseCustomPrice = parseFloat(form.dataset.basePrice || 349);
        const priceDisplay = document.getElementById('customStudioFinalPrice');
        const mockupFrame = document.getElementById('customMockupFrame');

        function updateCustomStudioPrice() {
            const selSize = form.querySelector('input[name="size"]:checked');
            const selFrame = form.querySelector('input[name="frame"]:checked');
            const qtyInput = form.querySelector('input[name="quantity"]');
            const qty = qtyInput ? parseInt(qtyInput.value) || 1 : 1;

            const sizeExtra = selSize ? parseFloat(selSize.dataset.extraPrice || 0) : 0;
            const frameExtra = selFrame ? parseFloat(selFrame.dataset.extraPrice || 0) : 0;
            const frameType = selFrame ? selFrame.dataset.frameType : 'none';

            const unit = baseCustomPrice + sizeExtra + frameExtra;
            const total = unit * qty;

            if (priceDisplay) {
                priceDisplay.innerText = `₹${total.toFixed(0)}`;
            }

            if (mockupFrame) {
                mockupFrame.className = `mockup-poster-frame frame-${frameType}`;
            }
        }

        form.querySelectorAll('input[name="size"], input[name="frame"]').forEach(el => {
            el.addEventListener('change', updateCustomStudioPrice);
        });
        const qtyInp = form.querySelector('input[name="quantity"]');
        if (qtyInp) qtyInp.addEventListener('input', updateCustomStudioPrice);

        updateCustomStudioPrice();
    }
}
