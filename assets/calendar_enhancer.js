// Seletor de Mês/Ano customizado para DatePickerSingle
window.dashExtensions = window.dashExtensions || {};

window.dashExtensions.initCalendarEnhancer = function() {
    let monthYearSelector = null;
    let currentDatePicker = null;

    // Função para criar o seletor de mês/ano
    function createMonthYearSelector() {
        if (monthYearSelector) return monthYearSelector;

        const selector = document.createElement('div');
        selector.className = 'custom-month-year-selector';
        selector.style.cssText = `
            position: absolute;
            background: #1e293b;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            z-index: 10000;
            display: none;
            min-width: 280px;
        `;

        // Header com navegação de ano
        const yearNav = document.createElement('div');
        yearNav.style.cssText = `
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        `;

        const prevYearBtn = createNavButton('◀', 'Ano anterior');
        const yearDisplay = document.createElement('div');
        yearDisplay.className = 'year-display';
        yearDisplay.style.cssText = `
            color: white;
            font-size: 1.1rem;
            font-weight: 600;
            text-align: center;
            flex: 1;
        `;
        const nextYearBtn = createNavButton('▶', 'Próximo ano');

        yearNav.appendChild(prevYearBtn);
        yearNav.appendChild(yearDisplay);
        yearNav.appendChild(nextYearBtn);

        // Grid de meses
        const monthsGrid = document.createElement('div');
        monthsGrid.className = 'months-grid';
        monthsGrid.style.cssText = `
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            margin-bottom: 15px;
        `;

        const monthNames = ['jan.', 'fev.', 'mar.', 'abr.', 'mai.', 'jun.', 
                           'jul.', 'ago.', 'set.', 'out.', 'nov.', 'dez.'];

        monthNames.forEach((month, index) => {
            const monthBtn = document.createElement('button');
            monthBtn.textContent = month;
            monthBtn.dataset.month = index;
            monthBtn.className = 'month-selector-btn';
            monthBtn.style.cssText = `
                background: #334155;
                color: #e2e8f0;
                border: none;
                border-radius: 8px;
                padding: 10px 8px;
                font-size: 0.9rem;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                text-transform: lowercase;
            `;
            monthBtn.onmouseover = () => {
                if (!monthBtn.classList.contains('active')) {
                    monthBtn.style.background = '#475569';
                }
            };
            monthBtn.onmouseout = () => {
                if (!monthBtn.classList.contains('active')) {
                    monthBtn.style.background = '#334155';
                }
            };
            monthsGrid.appendChild(monthBtn);
        });

        // Botão Limpar
        const clearBtn = document.createElement('button');
        clearBtn.textContent = 'Limpar';
        clearBtn.style.cssText = `
            width: 100%;
            background: #475569;
            color: white;
            border: 1px solid #64748b;
            border-radius: 8px;
            padding: 10px;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        `;
        clearBtn.onmouseover = () => clearBtn.style.background = '#334155';
        clearBtn.onmouseout = () => clearBtn.style.background = '#475569';

        selector.appendChild(yearNav);
        selector.appendChild(monthsGrid);
        selector.appendChild(clearBtn);

        monthYearSelector = selector;
        return selector;
    }

    function createNavButton(text, title) {
        const btn = document.createElement('button');
        btn.textContent = text;
        btn.title = title;
        btn.style.cssText = `
            background: #334155;
            color: white;
            border: none;
            border-radius: 6px;
            width: 36px;
            height: 36px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 0.9rem;
        `;
        btn.onmouseover = () => {
            btn.style.background = '#3b82f6';
            btn.style.transform = 'scale(1.05)';
        };
        btn.onmouseout = () => {
            btn.style.background = '#334155';
            btn.style.transform = 'scale(1)';
        };
        return btn;
    }

    function showMonthYearSelector(caption, datePickerInput) {
        const selector = createMonthYearSelector();
        currentDatePicker = datePickerInput;

        // Parse current date or use today
        let currentDate = new Date();
        const inputValue = datePickerInput.value;
        if (inputValue && inputValue.match(/\d{2}\/\d{2}\/\d{4}/)) {
            const parts = inputValue.split('/');
            currentDate = new Date(parts[2], parts[1] - 1, parts[0]);
        }

        let selectedYear = currentDate.getFullYear();
        let selectedMonth = currentDate.getMonth();

        const yearDisplay = selector.querySelector('.year-display');
        const monthButtons = selector.querySelectorAll('.month-selector-btn');
        const prevYearBtn = selector.querySelector('button[title="Ano anterior"]');
        const nextYearBtn = selector.querySelector('button[title="Próximo ano"]');
        const clearBtn = selector.querySelector('button:last-child');

        function updateDisplay() {
            yearDisplay.textContent = selectedYear;
            monthButtons.forEach((btn, index) => {
                if (index === selectedMonth) {
                    btn.style.background = '#3b82f6';
                    btn.style.color = 'white';
                    btn.classList.add('active');
                } else {
                    btn.style.background = '#334155';
                    btn.style.color = '#e2e8f0';
                    btn.classList.remove('active');
                }
            });
        }

        prevYearBtn.onclick = () => {
            selectedYear--;
            updateDisplay();
        };

        nextYearBtn.onclick = () => {
            selectedYear++;
            updateDisplay();
        };

        monthButtons.forEach((btn) => {
            btn.onclick = () => {
                selectedMonth = parseInt(btn.dataset.month);
                updateDisplay();
                
                // Navegar para o mês/ano selecionado
                navigateToMonthYear(selectedYear, selectedMonth);
                
                setTimeout(() => {
                    hideMonthYearSelector();
                }, 200);
            };
        });

        clearBtn.onclick = () => {
            datePickerInput.value = '';
            const event = new Event('change', { bubbles: true });
            datePickerInput.dispatchEvent(event);
            hideMonthYearSelector();
        };

        // Posicionar o seletor com ajuste para evitar overflow
        const rect = caption.getBoundingClientRect();
        const modalBody = caption.closest('.modal-body');
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        
        selector.style.display = 'block';
        selector.style.position = 'fixed';
        
        // Calcular posição horizontal (centralizar se necessário)
        let leftPos = rect.left;
        const selectorWidth = 280; // min-width definido no CSS
        
        // Se ultrapassar a direita, ajustar para a esquerda
        if (leftPos + selectorWidth > viewportWidth - 20) {
            leftPos = viewportWidth - selectorWidth - 20;
        }
        
        // Se ultrapassar a esquerda, ajustar para a direita
        if (leftPos < 20) {
            leftPos = 20;
        }
        
        // Calcular posição vertical
        let topPos = rect.bottom + 5;
        
        // Se ultrapassar a parte inferior, mostrar acima
        if (topPos + 300 > viewportHeight) {
            topPos = rect.top - 305;
        }
        
        selector.style.left = leftPos + 'px';
        selector.style.top = topPos + 'px';

        document.body.appendChild(selector);
        updateDisplay();
    }

    function hideMonthYearSelector() {
        if (monthYearSelector && monthYearSelector.parentNode) {
            monthYearSelector.style.display = 'none';
        }
    }

    function navigateToMonthYear(year, month) {
        const targetDate = new Date(year, month, 15);
        
        // Encontrar botões de navegação do calendário
        const calendarWrapper = currentDatePicker.closest('.SingleDatePicker');
        if (!calendarWrapper) return;

        const navButtons = calendarWrapper.querySelectorAll('.DayPickerNavigation_button');
        if (navButtons.length < 2) return;

        const prevBtn = navButtons[0];
        const nextBtn = navButtons[1];

        // Obter mês atual do calendário
        const caption = calendarWrapper.querySelector('.CalendarMonth_caption');
        if (!caption) return;

        let attempts = 0;
        const maxAttempts = 60; // Máximo 5 anos de navegação

        function clickUntilMonth() {
            if (attempts >= maxAttempts) return;
            
            const captionText = caption.textContent.trim();
            const currentDate = parsePortugueseDate(captionText);
            
            if (!currentDate) return;

            const currentYear = currentDate.getFullYear();
            const currentMonth = currentDate.getMonth();

            if (currentYear === year && currentMonth === month) {
                return; // Chegamos ao mês desejado
            }

            attempts++;

            if (targetDate > currentDate) {
                nextBtn.click();
            } else {
                prevBtn.click();
            }

            setTimeout(clickUntilMonth, 50);
        }

        clickUntilMonth();
    }

    function parsePortugueseDate(dateStr) {
        const months = {
            'janeiro': 0, 'fevereiro': 1, 'março': 2, 'abril': 3,
            'maio': 4, 'junho': 5, 'julho': 6, 'agosto': 7,
            'setembro': 8, 'outubro': 9, 'novembro': 10, 'dezembro': 11
        };

        const match = dateStr.match(/(\w+)\s+de\s+(\d{4})/);
        if (match) {
            const monthName = match[1].toLowerCase();
            const year = parseInt(match[2]);
            const month = months[monthName];
            if (month !== undefined) {
                return new Date(year, month, 1);
            }
        }
        return null;
    }

    // Observar mudanças no DOM para adicionar event listeners
    const observer = new MutationObserver(() => {
        const captions = document.querySelectorAll('.CalendarMonth_caption');
        captions.forEach(caption => {
            if (caption.dataset.enhanced) return;
            caption.dataset.enhanced = 'true';

            caption.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const dateInput = caption.closest('.SingleDatePicker')?.querySelector('.DateInput_input');
                if (dateInput) {
                    showMonthYearSelector(caption, dateInput);
                }
            });
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // Fechar seletor ao clicar fora
    document.addEventListener('click', (e) => {
        if (monthYearSelector && 
            monthYearSelector.style.display === 'block' &&
            !monthYearSelector.contains(e.target) &&
            !e.target.classList.contains('CalendarMonth_caption')) {
            hideMonthYearSelector();
        }
    });
};

// Inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.dashExtensions.initCalendarEnhancer);
} else {
    window.dashExtensions.initCalendarEnhancer();
}
