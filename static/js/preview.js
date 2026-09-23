// LinkStudio Appearance Studio Live Preview Engine (SaaS Edition)

document.addEventListener('DOMContentLoaded', () => {
  const previewIframe = document.getElementById('appearancePreviewFrame');
  if (!previewIframe) return;

  const themeSelector = document.getElementById('themeSelector');
  const bgTypeSelector = document.getElementById('bgTypeSelector');
  const bgColorInput = document.getElementById('bgColorInput');
  const bgGradientInput = document.getElementById('bgGradientInput');
  const bgOverlayInput = document.getElementById('bgOverlayInput');
  const bgOverlayDisplay = document.getElementById('bgOverlayDisplay');
  const bgBlurInput = document.getElementById('bgBlurInput');
  const bgBlurDisplay = document.getElementById('bgBlurDisplay');

  const textColorInput = document.getElementById('textColorInput');
  const buttonStyleSelector = document.getElementById('buttonStyleSelector');
  const buttonShapeSelector = document.getElementById('buttonShapeSelector');
  const cardShadowSelector = document.getElementById('cardShadowSelector');
  const hoverEffectSelector = document.getElementById('hoverEffectSelector');
  const buttonColorInput = document.getElementById('buttonColorInput');
  const buttonTextColorInput = document.getElementById('buttonTextColorInput');
  const accentColorInput = document.getElementById('accentColorInput');

  const fontFamilySelector = document.getElementById('fontFamilySelector');
  const avatarShapeSelector = document.getElementById('avatarShapeSelector');
  const avatarBorderSelector = document.getElementById('avatarBorderSelector');
  const alignmentSelector = document.getElementById('alignmentSelector');

  const socialPositionSelector = document.getElementById('socialPositionSelector');
  const socialStyleSelector = document.getElementById('socialStyleSelector');

  const bgImageInput = document.getElementById('bgImageInput') || document.querySelector('input[name="bg_image"]');
  const bannerImageInput = document.getElementById('bannerImageInput') || document.querySelector('input[name="banner_image"]');

  let currentBgImageData = null;
  let currentBannerImageData = null;

  // 1. Visual Theme Selection Cards Sync
  const themeCards = document.querySelectorAll('.theme-card-option');
  themeCards.forEach(card => {
    card.addEventListener('click', () => {
      const themeKey = card.getAttribute('data-theme-key');
      if (themeSelector) {
        themeSelector.value = themeKey;
      }

      // Highlight active card
      themeCards.forEach(c => {
        c.classList.remove('border-primary', 'ring-2', 'shadow-sm');
        c.classList.add('border');
      });
      card.classList.add('border-primary', 'ring-2', 'shadow-sm');
      card.classList.remove('border');

      // Update preview immediately
      updatePreview();
    });
  });

  // 2. Real-time Live Preview Updater
  function updatePreview() {
    try {
      const doc = previewIframe.contentDocument || previewIframe.contentWindow.document;
      if (!doc || !doc.body) return;

      const pageContainer = doc.getElementById('creatorPageRoot') || doc.querySelector('.creator-page');
      const bgLayer = doc.getElementById('creatorBgLayer');
      const overlayLayer = doc.getElementById('creatorBgOverlay') || doc.querySelector('.creator-bg-overlay');
      const avatar = doc.querySelector('.creator-avatar');
      const header = doc.querySelector('header');
      const links = doc.querySelectorAll('.creator-link-btn');
      const cards = doc.querySelectorAll('.theme-card');
      const buttons = doc.querySelectorAll('.btn');
      const socialsTop = doc.getElementById('socialsTopContainer');
      const socialsBottom = doc.getElementById('socialsBottomContainer');
      const socialIcons = doc.querySelectorAll('.social-icon-circle');
      let bannerWrapper = doc.querySelector('.creator-banner-wrapper');

      if (!pageContainer) return;

      // Theme class
      if (themeSelector && themeSelector.value) {
        pageContainer.className = pageContainer.className.replace(/\btheme-\S+/g, '').trim();
        pageContainer.classList.add(`theme-${themeSelector.value}`);
      }

      // Font family class
      if (fontFamilySelector && fontFamilySelector.value) {
        pageContainer.className = pageContainer.className.replace(/\bfont-\S+/g, '').trim();
        pageContainer.classList.add(`font-${fontFamilySelector.value}`);
      }

      // Background Rendering
      const targetBg = bgLayer || pageContainer;
      if (currentBgImageData) {
        targetBg.style.background = `url('${currentBgImageData}') center / cover no-repeat`;
        if (overlayLayer) overlayLayer.style.display = 'block';
      } else if (bgTypeSelector && bgTypeSelector.value === 'color' && bgColorInput) {
        targetBg.style.background = bgColorInput.value;
        if (overlayLayer) overlayLayer.style.display = 'none';
      } else if (bgTypeSelector && bgTypeSelector.value === 'gradient' && bgGradientInput) {
        targetBg.style.background = bgGradientInput.value;
        if (overlayLayer) overlayLayer.style.display = 'none';
      } else if (bgTypeSelector && bgTypeSelector.value === 'theme') {
        targetBg.style.background = '';
        if (overlayLayer) overlayLayer.style.display = 'none';
      }

      // Background Overlay (Darkness & Blur)
      if (overlayLayer) {
        const opacityVal = bgOverlayInput ? bgOverlayInput.value : '30';
        const blurVal = bgBlurInput ? bgBlurInput.value : '0';
        overlayLayer.style.backgroundColor = `rgba(0, 0, 0, ${opacityVal / 100})`;
        overlayLayer.style.backdropFilter = `blur(${blurVal}px)`;
        overlayLayer.style.webkitBackdropFilter = `blur(${blurVal}px)`;
      }

      // Text and Accent Colors
      if (textColorInput) {
        pageContainer.style.color = textColorInput.value;
      }
      if (accentColorInput) {
        pageContainer.style.setProperty('--theme-accent', accentColorInput.value);
      }
      if (buttonColorInput) {
        pageContainer.style.setProperty('--btn-color', buttonColorInput.value);
      }
      if (buttonTextColorInput) {
        pageContainer.style.setProperty('--btn-text', buttonTextColorInput.value);
      }

      // Avatar Shape & Border
      if (avatar) {
        if (avatarShapeSelector) {
          avatar.className = avatar.className.replace(/\bavatar-(circle|rounded|square)\b/g, '').trim();
          avatar.classList.add(`avatar-${avatarShapeSelector.value}`);
        }
        if (avatarBorderSelector) {
          avatar.className = avatar.className.replace(/\bavatar-border-\S+/g, '').trim();
          avatar.classList.add(`avatar-border-${avatarBorderSelector.value}`);
        }
      }

      // Alignment
      if (header && alignmentSelector) {
        if (alignmentSelector.value === 'left') {
          header.className = header.className.replace(/\btext-center\b/g, 'text-start');
          header.classList.remove('align-items-center');
          header.classList.add('align-items-start');
          if (socialsTop) {
            socialsTop.classList.remove('justify-content-center');
            socialsTop.classList.add('justify-content-start');
          }
        } else {
          header.className = header.className.replace(/\btext-start\b/g, 'text-center');
          header.classList.remove('align-items-start');
          header.classList.add('align-items-center');
          if (socialsTop) {
            socialsTop.classList.remove('justify-content-start');
            socialsTop.classList.add('justify-content-center');
          }
        }
      }

      // Social Icons Position
      if (socialPositionSelector) {
        if (socialPositionSelector.value === 'bottom') {
          if (socialsTop) socialsTop.style.setProperty('display', 'none', 'important');
          if (socialsBottom) socialsBottom.style.removeProperty('display');
        } else {
          if (socialsBottom) socialsBottom.style.setProperty('display', 'none', 'important');
          if (socialsTop) socialsTop.style.removeProperty('display');
        }
      }

      // Social Icons Style
      if (socialStyleSelector) {
        socialIcons.forEach(icon => {
          icon.className = icon.className.replace(/\bsocial-style-\S+/g, '').trim();
          icon.classList.add(`social-style-${socialStyleSelector.value}`);
        });
      }

      // Card & Button Shapes, Styles, Shadows, and Hover Effects
      links.forEach(link => {
        // Shape
        if (buttonShapeSelector) {
          link.className = link.className.replace(/\bshape-\S+/g, '').trim();
          link.classList.add(`shape-${buttonShapeSelector.value}`);
        }
        // Style
        if (buttonStyleSelector) {
          link.className = link.className.replace(/\bstyle-\S+/g, '').trim();
          link.classList.add(`style-${buttonStyleSelector.value}`);
        }
        // Shadow
        if (cardShadowSelector) {
          link.className = link.className.replace(/\bshadow-\S+/g, '').trim();
          link.classList.add(`shadow-${cardShadowSelector.value}`);
        }
        // Hover
        if (hoverEffectSelector) {
          link.className = link.className.replace(/\bhover-\S+/g, '').trim();
          link.classList.add(`hover-${hoverEffectSelector.value}`);
        }
      });

      // Cards shape and shadow
      cards.forEach(card => {
        if (buttonShapeSelector) {
          card.className = card.className.replace(/\bshape-\S+/g, '').trim();
          card.classList.add(`shape-${buttonShapeSelector.value}`);
        }
        if (cardShadowSelector) {
          card.className = card.className.replace(/\bshadow-\S+/g, '').trim();
          card.classList.add(`shadow-${cardShadowSelector.value}`);
        }
      });

      // All buttons shape
      if (buttonShapeSelector) {
        buttons.forEach(btn => {
          btn.className = btn.className.replace(/\bshape-\S+/g, '').trim();
          btn.classList.add(`shape-${buttonShapeSelector.value}`);
        });
      }

      // Banner Cover Live Preview
      if (currentBannerImageData) {
        const container = doc.querySelector('.creator-container');
        if (!bannerWrapper) {
          bannerWrapper = doc.createElement('div');
          bannerWrapper.className = 'creator-banner-wrapper';
          const bannerImg = doc.createElement('img');
          bannerImg.className = 'creator-banner-img';
          bannerImg.src = currentBannerImageData;
          bannerWrapper.appendChild(bannerImg);
          if (container && container.parentNode) {
            container.parentNode.insertBefore(bannerWrapper, container);
            container.classList.add('has-banner');
            if (header) header.classList.add('creator-header-with-banner');
          }
        } else {
          const bannerImg = bannerWrapper.querySelector('.creator-banner-img');
          if (bannerImg) bannerImg.src = currentBannerImageData;
        }
      }

    } catch (e) {
      console.warn('Preview sync warning:', e);
    }
  }

  // 3. File Input Handlers (FileReader for instant visual reaction)
  if (bgImageInput) {
    bgImageInput.addEventListener('change', (e) => {
      const file = e.target.files && e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          currentBgImageData = event.target.result;
          if (bgTypeSelector) bgTypeSelector.value = 'image';
          updatePreview();
        };
        reader.readAsDataURL(file);
      }
    });
  }

  if (bannerImageInput) {
    bannerImageInput.addEventListener('change', (e) => {
      const file = e.target.files && e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          currentBannerImageData = event.target.result;
          updatePreview();
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // 4. Slider Display Labels Real-Time Handlers
  if (bgOverlayInput && bgOverlayDisplay) {
    bgOverlayInput.addEventListener('input', () => {
      bgOverlayDisplay.textContent = `${bgOverlayInput.value}%`;
      updatePreview();
    });
  }

  if (bgBlurInput && bgBlurDisplay) {
    bgBlurInput.addEventListener('input', () => {
      bgBlurDisplay.textContent = `${bgBlurInput.value}px`;
      updatePreview();
    });
  }

  // 5. Input Listeners
  const allInputs = [
    themeSelector, bgTypeSelector, bgColorInput, bgGradientInput,
    textColorInput, buttonStyleSelector, buttonShapeSelector,
    cardShadowSelector, hoverEffectSelector,
    buttonColorInput, buttonTextColorInput, accentColorInput,
    fontFamilySelector, avatarShapeSelector, avatarBorderSelector,
    alignmentSelector, socialPositionSelector, socialStyleSelector
  ];

  allInputs.forEach(input => {
    if (input) {
      input.addEventListener('input', () => {
        if (input === bgTypeSelector && input.value !== 'image') {
          currentBgImageData = null;
        }
        updatePreview();
      });
      input.addEventListener('change', () => {
        if (input === bgTypeSelector && input.value !== 'image') {
          currentBgImageData = null;
        }
        updatePreview();
      });
    }
  });

  // Re-sync whenever iframe loads
  previewIframe.addEventListener('load', () => {
    setTimeout(updatePreview, 250);
  });
});
