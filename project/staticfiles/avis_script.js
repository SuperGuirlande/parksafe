document.addEventListener('DOMContentLoaded', function() {
    const avisContainer = document.getElementById('avisContainer');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const cards = document.querySelectorAll('.avis-card');

if (avisContainer && cards.length > 0) {
    let currentIndex = 0;
    let cardsPerView = 1;

    function updateCardsPerView() {
        cardsPerView = window.innerWidth >= 1280 ? 3 : 1;
    }

    function getCardWidth() {
        return window.innerWidth >= 1280 ? 400 : window.innerWidth * 0.9;
    }

    function updateSlidePosition() {
        const cardWidth = getCardWidth();
        const gap = window.innerWidth >= 1280 ? 20 : 10;
        const maxIndex = Math.max(0, cards.length - cardsPerView);

        currentIndex = Math.min(currentIndex, maxIndex);
        avisContainer.style.transform = `translateX(-${currentIndex * (cardWidth + gap)}px)`;

        if (prevBtn) {
            prevBtn.disabled = currentIndex === 0;
        }
        if (nextBtn) {
            nextBtn.disabled = currentIndex >= maxIndex;
        }
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentIndex > 0) {
                currentIndex--;
                updateSlidePosition();
            }
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            if (currentIndex < cards.length - cardsPerView) {
                currentIndex++;
                updateSlidePosition();
            }
        });
    }

    updateCardsPerView();
    updateSlidePosition();

    let timeout;
    window.addEventListener('resize', () => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            const previousCardsPerView = cardsPerView;
            updateCardsPerView();

            if (currentIndex > cards.length - cardsPerView) {
                currentIndex = Math.max(0, cards.length - cardsPerView);
            }

            if (previousCardsPerView !== cardsPerView) {
                updateSlidePosition();
            }
        }, 150);
    });
}

});