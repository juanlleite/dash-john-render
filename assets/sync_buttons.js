// Sincronização automática de botões com linhas da tabela
window.dashExtensions = window.dashExtensions || {};

window.dashExtensions.syncTableButtons = function() {
    function adjustButtonPositions() {
        const table = document.querySelector('#customers-table');
        const buttonsWrapper = document.querySelector('.action-buttons-wrapper');
        
        if (!table || !buttonsWrapper) return;
        
        const tableRows = table.querySelectorAll('tbody tr');
        const buttonRows = buttonsWrapper.querySelectorAll('.action-btn-row');
        
        // Ajustar altura de cada botão para corresponder à linha da tabela
        tableRows.forEach((row, index) => {
            if (buttonRows[index]) {
                const rowHeight = row.offsetHeight;
                buttonRows[index].style.height = rowHeight + 'px';
            }
        });
    }
    
    // Executar após renderização
    const observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            if (mutation.type === 'childList' || mutation.type === 'attributes') {
                setTimeout(adjustButtonPositions, 100);
                break;
            }
        }
    });
    
    // Observar mudanças na tabela e nos botões
    const tableContainer = document.querySelector('.table-container');
    if (tableContainer) {
        observer.observe(tableContainer, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['style']
        });
    }
    
    // Executar imediatamente e após resize
    adjustButtonPositions();
    window.addEventListener('resize', adjustButtonPositions);
    
    // Re-executar periodicamente para garantir sincronização
    setInterval(adjustButtonPositions, 1000);
};

// Inicializar
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.dashExtensions.syncTableButtons);
} else {
    window.dashExtensions.syncTableButtons();
}
