const pages = document.querySelectorAll('.page');
const servicesToggle = document.getElementById('services-toggle');
const servicesSubmenu = document.getElementById('services-submenu');
const feedbackForm = document.getElementById('feedback-form');
const statusEl = document.getElementById('form-status');
const serviceField = document.getElementById('serviceField');

const servicesData = {
  'service-web-dev': [
    {
      title: 'Старт',
      badge: 'НАЧАЛЬНЫЙ САЙТ',
      desc: 'Подходит для бизнеса или личного бренда.',
      price: '₽20 000',
      includes: ['Лендинг или визитка', 'Базовая SEO-настройка'],
    },
    {
      title: 'База',
      badge: 'САМЫЙ ПОПУЛЯРНЫЙ',
      blue: true,
      desc: 'Сайт с рекламной структурой и аналитикой.',
      price: '₽30 000',
      includes: ['Многостраничный сайт', 'Настройка рекламы'],
    },
    {
      title: 'Профи',
      badge: 'ПРОФЕССИОНАЛЬНЫЙ',
      desc: 'Индивидуальный дизайн и автоматизация.',
      price: 'от ₽60 000',
      includes: ['CRM/бот интеграции', 'Поддержка запуска'],
    },
  ],
  'service-web-promo': [
    {
      title: 'База',
      badge: 'УВЕЛИЧЕНИЕ ОХВАТА',
      desc: 'Рост посещений, заявок и продаж.',
      price: '₽20 000/мес',
      includes: ['Контент-план', 'Базовая реклама'],
    },
    {
      title: 'Плюс',
      badge: 'ПРЕМИУМ',
      blue: true,
      desc: 'Детальная проработка каналов трафика.',
      price: '₽40 000/мес',
      includes: ['Ретаргетинг', 'Оптимизация воронки'],
    },
    {
      title: 'Профи',
      badge: 'ВЕДУЩИЕ СМИ',
      desc: 'PR в медиа и репутационная поддержка.',
      price: '₽60 000/мес',
      includes: ['Публикации в СМИ', 'Стратегия бренда'],
    },
  ],
  'service-app-dev': [
    {
      title: 'Старт',
      badge: 'БАЗОВОЕ ПРИЛОЖЕНИЕ',
      desc: 'MVP с базовым функционалом.',
      price: '₽50 000',
      includes: ['UX-прототип', 'Публикация в сторах'],
    },
    {
      title: 'База',
      badge: 'САМЫЙ ПОПУЛЯРНЫЙ',
      blue: true,
      desc: '2D/сервисные приложения под задачи бизнеса.',
      price: '₽75 000',
      includes: ['Панель управления', 'Аналитика'],
    },
    {
      title: 'Профи',
      badge: 'ПРОФЕССИОНАЛЬНЫЙ',
      desc: 'Полный цикл с интеграциями и поддержкой.',
      price: 'от ₽100 000',
      includes: ['2D/3D модули', 'Интеграции с сервисами'],
    },
  ],
  'service-app-promo': [
    {
      title: 'Старт',
      badge: 'БАЗОВОЕ ПРОДВИЖЕНИЕ',
      desc: 'Органический рост аудитории приложения.',
      price: '₽25 000/мес',
      includes: ['ASO база', 'План публикаций'],
    },
    {
      title: 'База',
      badge: 'САМЫЙ ПОПУЛЯРНЫЙ',
      blue: true,
      desc: 'Рекламные запуски и коллаборации.',
      price: '₽40 000/мес',
      includes: ['Инфлюенсер-каналы', 'A/B тесты'],
    },
    {
      title: 'Профи',
      badge: 'ПРОФЕССИОНАЛЬНЫЙ',
      desc: 'Продуктовый маркетинг и масштабирование.',
      price: '₽60 000/мес',
      includes: ['Персональный продакт-план', 'Рост LTV'],
    },
  ],
  combo: [
    {
      title: 'ВебПро',
      badge: 'ПОЛНОЕ ОБСЛУЖИВАНИЕ САЙТА',
      desc: 'Создание сайта и его продвижение.',
      price: '₽55 000',
      includes: ['Разработка сайта пакет “База”', 'Продвижение сайта пакет “База”'],
    },
    {
      title: 'ВебАпп',
      badge: 'СОЗДАНИЕ IT СИСТЕМЫ',
      blue: true,
      desc: 'Создание сайта и приложения.',
      price: '₽70 000',
      includes: ['Сайт пакет “База”', 'Приложение пакет “Старт”'],
    },
    {
      title: 'СоцВеб',
      badge: 'МАКСИМАЛЬНЫЙ ОХВАТ АУДИТОРИИ',
      desc: 'Продвижение соцсетей и сайта.',
      price: '₽55 000',
      includes: ['SMM пакет “База”', 'Продвижение сайта пакет “База”'],
    },
  ],
};

function renderCards(pageId, cards) {
  const container = document.querySelector(`#${pageId} .cards`);
  if (!container) return;
  container.innerHTML = cards
    .map(
      (card) => `
      <article class="card">
        <div class="card-head">
          <span class="badge ${card.blue ? 'blue' : ''}">${card.badge}</span>
          <h3>${card.title}</h3>
          <p>${card.desc}</p>
        </div>
        <div class="price">${card.price}</div>
        <ul class="includes">${card.includes.map((item) => `<li>${item}</li>`).join('')}</ul>
        <button class="order-btn" data-service="${pageId}: ${card.title}">Заказать</button>
      </article>
    `,
    )
    .join('');
}

Object.entries(servicesData).forEach(([pageId, cards]) => renderCards(pageId, cards));

function showPage(id) {
  pages.forEach((page) => page.classList.toggle('active', page.id === id));
  if (id !== 'home') {
    servicesSubmenu.classList.add('hidden');
  }
}

document.body.addEventListener('click', (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) return;

  if (target.matches('[data-target]')) {
    const pageId = target.dataset.target;
    if (pageId) showPage(pageId);
  }

  if (target.matches('.back-btn')) {
    showPage('home');
  }

  if (target.matches('.order-btn')) {
    serviceField.value = target.dataset.service || '';
    statusEl.textContent = '';
    feedbackForm.reset();
    serviceField.value = target.dataset.service || '';
    showPage('feedback');
  }
});

servicesToggle?.addEventListener('click', () => {
  servicesSubmenu.classList.toggle('hidden');
});

feedbackForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  statusEl.textContent = 'Отправляем...';

  const formData = new FormData(feedbackForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    const response = await fetch('/api/contact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const result = await response.json();
    if (!response.ok || !result.ok) {
      throw new Error(result.error || 'Ошибка отправки');
    }

    statusEl.textContent = '✅ Заявка отправлена владельцу @threelives';
    feedbackForm.reset();
  } catch (error) {
    statusEl.textContent = `❌ ${(error).message}`;
  }
});
