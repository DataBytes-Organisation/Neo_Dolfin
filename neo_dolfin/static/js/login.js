let currentCard = 0;
let intervalId;

function showCard(direction) 
{
    clearInterval(intervalId); // Clear the interval

    const cardContainer = document.getElementById('card-container');
    const cards = cardContainer.getElementsByClassName('card');
    const dots = document.getElementsByClassName('dot');
    const totalCards = cards.length;

    if (direction === 'prev')
    {
        currentCard = (currentCard - 1 + totalCards) % totalCards;
    }
    else if (direction === 'next') 
    {
        currentCard = (currentCard + 1) % totalCards;
    }

    for (let i = 0; i < totalCards; i++) 
    {
        if (i === currentCard) 
        {
            cards[i].style.display = 'block';
            dots[i].classList.add('active');
        }
        else 
        {
            cards[i].style.display = 'none';
            dots[i].classList.remove('active');
        }
    }

    // Set a new interval for auto-navigation
    intervalId = setInterval(() => showCard('next'), 5000);
}

function goToCard(index) 
{
    currentCard = index;
    showCard();
}

// Initial auto-navigation setup
showCard();