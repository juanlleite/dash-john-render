// Calendário Customizado Completo para Dash
(function() {
    'use strict';

    const monthNames = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                       'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
    const monthNamesShort = ['jan.', 'fev.', 'mar.', 'abr.', 'mai.', 'jun.',
                            'jul.', 'ago.', 'set.', 'out.', 'nov.', 'dez.'];
    const dayNames = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

    class CustomCalendar {
        constructor(inputElement) {
            this.input = inputElement;
            this.selectedDate = null;
            this.currentMonth = new Date().getMonth();
            this.currentYear = new Date().getFullYear();
            this.isOpen = false;
            this.calendar = null;
            this.yearMonthSelector = null;
            
            this.init();
        }

        init() {
            // Adicionar ícone ao input
            this.input.style.paddingRight = '40px';
            this.input.style.cursor = 'pointer';
            this.input.readOnly = true;
            
            // Parse data inicial se existir
            if (this.input.value) {
                const date = this.parseDate(this.input.value);
                if (date) {
                    this.selectedDate = date;
                    this.currentMonth = date.getMonth();
                    this.currentYear = date.getFullYear();
                }
            }

            // Event listeners
            this.input.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggle();
            });

            // Fechar ao clicar fora
            document.addEventListener('click', (e) => {
                if (this.isOpen && !this.calendar?.contains(e.target) && e.target !== this.input) {
                    this.close();
                }
            });
        }

        parseDate(str) {
            // Formato: dd/mm/yyyy
            const parts = str.split('/');
            if (parts.length === 3) {
                const day = parseInt(parts[0]);
                const month = parseInt(parts[1]) - 1;
                const year = parseInt(parts[2]);
                if (!isNaN(day) && !isNaN(month) && !isNaN(year)) {
                    return new Date(year, month, day);
                }
            }
            return null;
        }

        formatDate(date) {
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const year = date.getFullYear();
            return `${day}/${month}/${year}`;
        }

        toggle() {
            if (this.isOpen) {
                this.close();
            } else {
                this.open();
            }
        }

        open() {
            this.isOpen = true;
            this.createCalendar();
            this.positionCalendar();
        }

        close() {
            if (this.calendar) {
                this.calendar.remove();
                this.calendar = null;
            }
            if (this.yearMonthSelector) {
                this.yearMonthSelector.remove();
                this.yearMonthSelector = null;
            }
            this.isOpen = false;
        }

        createCalendar() {
            if (this.calendar) {
                this.calendar.remove();
            }

            this.calendar = document.createElement('div');
            this.calendar.className = 'custom-calendar-popup';
            this.calendar.innerHTML = `
                <div class="calendar-header">
                    <button class="calendar-nav-btn" data-action="prev-month">
                        <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
                            <path d="M7.5 2L3.5 6L7.5 10"/>
                        </svg>
                    </button>
                    <button class="calendar-month-year-btn">
                        ${monthNames[this.currentMonth]} de ${this.currentYear}
                    </button>
                    <button class="calendar-nav-btn" data-action="next-month">
                        <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
                            <path d="M4.5 2L8.5 6L4.5 10"/>
                        </svg>
                    </button>
                </div>
                <div class="calendar-weekdays">
                    ${dayNames.map(day => `<div class="calendar-weekday">${day}</div>`).join('')}
                </div>
                <div class="calendar-days"></div>
                <div class="calendar-footer">
                    <button class="calendar-clear-btn">Limpar</button>
                </div>
            `;

            // Event listeners
            this.calendar.querySelector('[data-action="prev-month"]').addEventListener('click', () => {
                this.currentMonth--;
                if (this.currentMonth < 0) {
                    this.currentMonth = 11;
                    this.currentYear--;
                }
                this.updateCalendar();
            });

            this.calendar.querySelector('[data-action="next-month"]').addEventListener('click', () => {
                this.currentMonth++;
                if (this.currentMonth > 11) {
                    this.currentMonth = 0;
                    this.currentYear++;
                }
                this.updateCalendar();
            });

            this.calendar.querySelector('.calendar-month-year-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                this.showYearMonthSelector();
            });

            this.calendar.querySelector('.calendar-clear-btn').addEventListener('click', () => {
                this.selectedDate = null;
                this.input.value = '';
                this.input.dispatchEvent(new Event('change', { bubbles: true }));
                this.close();
            });

            this.updateCalendar();
            document.body.appendChild(this.calendar);
        }

        updateCalendar() {
            const daysContainer = this.calendar.querySelector('.calendar-days');
            daysContainer.innerHTML = '';

            const firstDay = new Date(this.currentYear, this.currentMonth, 1);
            const lastDay = new Date(this.currentYear, this.currentMonth + 1, 0);
            const prevLastDay = new Date(this.currentYear, this.currentMonth, 0);

            const firstDayIndex = firstDay.getDay();
            const lastDayDate = lastDay.getDate();
            const prevLastDayDate = prevLastDay.getDate();

            // Dias do mês anterior
            for (let i = firstDayIndex - 1; i >= 0; i--) {
                const day = prevLastDayDate - i;
                const dayEl = this.createDayElement(day, true);
                daysContainer.appendChild(dayEl);
            }

            // Dias do mês atual
            for (let day = 1; day <= lastDayDate; day++) {
                const dayEl = this.createDayElement(day, false);
                daysContainer.appendChild(dayEl);
            }

            // Dias do próximo mês
            const totalCells = daysContainer.children.length;
            const remainingCells = 42 - totalCells; // 6 semanas
            for (let day = 1; day <= remainingCells; day++) {
                const dayEl = this.createDayElement(day, true);
                daysContainer.appendChild(dayEl);
            }

            // Atualizar texto do botão
            this.calendar.querySelector('.calendar-month-year-btn').textContent = 
                `${monthNames[this.currentMonth]} de ${this.currentYear}`;
        }

        createDayElement(day, isOtherMonth) {
            const dayEl = document.createElement('button');
            dayEl.className = 'calendar-day';
            dayEl.textContent = day;

            if (isOtherMonth) {
                dayEl.classList.add('other-month');
            } else {
                const date = new Date(this.currentYear, this.currentMonth, day);
                
                // Marcar dia selecionado
                if (this.selectedDate && 
                    this.selectedDate.getDate() === day &&
                    this.selectedDate.getMonth() === this.currentMonth &&
                    this.selectedDate.getFullYear() === this.currentYear) {
                    dayEl.classList.add('selected');
                }

                // Marcar hoje
                const today = new Date();
                if (today.getDate() === day &&
                    today.getMonth() === this.currentMonth &&
                    today.getFullYear() === this.currentYear) {
                    dayEl.classList.add('today');
                }

                dayEl.addEventListener('click', () => {
                    this.selectDate(date);
                });
            }

            return dayEl;
        }

        selectDate(date) {
            this.selectedDate = date;
            this.input.value = this.formatDate(date);
            this.input.dispatchEvent(new Event('change', { bubbles: true }));
            this.close();
        }

        showYearMonthSelector() {
            if (this.yearMonthSelector) {
                this.yearMonthSelector.remove();
            }

            this.yearMonthSelector = document.createElement('div');
            this.yearMonthSelector.className = 'year-month-selector';
            
            const yearNav = document.createElement('div');
            yearNav.className = 'year-selector';
            yearNav.innerHTML = `
                <button class="year-nav-btn" data-action="prev-year">◀</button>
                <div class="year-display">${this.currentYear}</div>
                <button class="year-nav-btn" data-action="next-year">▶</button>
            `;

            const monthGrid = document.createElement('div');
            monthGrid.className = 'month-grid';
            monthNamesShort.forEach((month, index) => {
                const btn = document.createElement('button');
                btn.className = 'month-btn';
                btn.textContent = month;
                if (index === this.currentMonth) {
                    btn.classList.add('selected');
                }
                btn.addEventListener('click', () => {
                    this.currentMonth = index;
                    this.updateCalendar();
                    this.yearMonthSelector.remove();
                    this.yearMonthSelector = null;
                });
                monthGrid.appendChild(btn);
            });

            this.yearMonthSelector.appendChild(yearNav);
            this.yearMonthSelector.appendChild(monthGrid);

            // Event listeners para navegação de ano
            yearNav.querySelector('[data-action="prev-year"]').addEventListener('click', () => {
                this.currentYear--;
                yearNav.querySelector('.year-display').textContent = this.currentYear;
            });

            yearNav.querySelector('[data-action="next-year"]').addEventListener('click', () => {
                this.currentYear++;
                yearNav.querySelector('.year-display').textContent = this.currentYear;
            });

            // Posicionar
            const rect = this.calendar.getBoundingClientRect();
            this.yearMonthSelector.style.position = 'fixed';
            this.yearMonthSelector.style.left = rect.left + 'px';
            this.yearMonthSelector.style.top = rect.top + 'px';

            document.body.appendChild(this.yearMonthSelector);
        }

        positionCalendar() {
            const rect = this.input.getBoundingClientRect();
            const calendarHeight = 400;
            const spaceBelow = window.innerHeight - rect.bottom;
            const spaceAbove = rect.top;

            this.calendar.style.position = 'fixed';
            this.calendar.style.left = rect.left + 'px';
            this.calendar.style.zIndex = '10000';

            if (spaceBelow >= calendarHeight || spaceBelow > spaceAbove) {
                this.calendar.style.top = (rect.bottom + 5) + 'px';
            } else {
                this.calendar.style.bottom = (window.innerHeight - rect.top + 5) + 'px';
            }
        }
    }

    // Inicializar calendários customizados
    function initCustomCalendars() {
        const observer = new MutationObserver(() => {
            // Procurar por DatePickerSingle e substituir
            document.querySelectorAll('.DateInput_input').forEach(input => {
                if (!input.dataset.customCalendar) {
                    input.dataset.customCalendar = 'true';
                    new CustomCalendar(input);
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        // Inicializar imediatamente
        document.querySelectorAll('.DateInput_input').forEach(input => {
            if (!input.dataset.customCalendar) {
                input.dataset.customCalendar = 'true';
                new CustomCalendar(input);
            }
        });
    }

    // Iniciar quando DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCustomCalendars);
    } else {
        initCustomCalendars();
    }
})();
