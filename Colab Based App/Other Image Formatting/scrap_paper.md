// from js inside const style = document.createElement('style'):

style.textContent = ` 
    /* Keep the default modebar completely hidden/collapsed */ 
    .js-plotly-plot .plotly .modebar { 
        opacity: 0 !important; 
        pointer-events: none !important; 
        transform: translateX(20px); 
        transition: all 0.3s ease-in-out !important; 
    } 
    /* Expanded state when the single icon is toggled active */ 
    .js-plotly-plot.modebar-expanded .plotly .modebar { 
        opacity: 1 !important; 
        pointer-events: auto !important; 
    } 
    /* NEW: Re-aligns internal Plotly row groups into an absolute vertical stack */
    .js-plotly-plot.style-vertical-modebar .plotly .modebar {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        width: auto !important;
        background: transparent !important;
    }
    
    /* Forces the internal grouping rows to act as vertical columns */
    .js-plotly-plot.style-vertical-modebar .plotly .modebar-group {
        display: flex !important;
        flex-direction: column !important;
        padding: 0 !important;
        margin-bottom: 4px !important; /* Adds a clean gap between buttons */
    }
    
    /* The custom single icon container */ 
    .plotly-custom-toggle { 
        position: absolute; 
        top: 10px; 
        right: 8px; 
        z-index: 1001; 
        background: rgba(0, 0, 0, 0.7); 
        border-radius: 4px; 
        width: 25px; 
        height: 25px; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        cursor: pointer; 
        font-size: 16px; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.1); 
        transition: background 0.2s; 
        user-select: none; 
    } 
    .plotly-custom-toggle:hover { 
        background: rgba(42, 42, 62, 0.7); 
    } 
`; 
document.head.appendChild(style); 


// 2. Dynamically add the single toggle icon to every Plotly chart on the page 
document.addEventListener('DOMContentLoaded', () => { 
    // We use a MutationObserver to catch charts even if they load dynamically 
    const observer = new MutationObserver(() => { 
        const charts = document.querySelectorAll('.js-plotly-plot:not(.has-toggle-btn)'); 
        
        charts.forEach(chart => { 
            if (!chart.layout) return;
            
            chart.classList.add('has-toggle-btn'); 
            
            const layoutStyle = (chart.layout && chart.layout.meta && chart.layout.meta.modebar_style) || 'shifted';
            const modebar = chart.querySelector('.modebar');
            
            // NEW: Flags the chart element wrapper so CSS layout locks the vertical view
            if (layoutStyle === 'vertical') {
                chart.classList.add('style-vertical-modebar');
            }
            
            // Create the single collapse/expand icon 
            const toggleBtn = document.createElement('div'); 
            toggleBtn.className = 'plotly-custom-toggle'; 
            toggleBtn.innerHTML = '☰'; 
            
            // Handle clicking the single icon 
            toggleBtn.addEventListener('click', (e) => { 
                e.stopPropagation(); 
                chart.classList.toggle('modebar-expanded'); 
                
                const isOpen = chart.classList.contains('modebar-expanded');
                toggleBtn.innerHTML = isOpen ? '✕' : '☰'; 
                
                if (modebar) {
                    if (isOpen) {
                        if (layoutStyle === 'vertical') {
                            // Perfect drop spacing below your close button
                            modebar.style.setProperty('transform', 'translateY(35px) translateX(-5px)', 'important');
                        } else {
                            // Left shift for horizontal bars to clear the close icon
                            modebar.style.setProperty('transform', 'translateX(-45px)', 'important');
                        }
                    } else {
                        // Reset layout back to default when collapsed
                        modebar.style.setProperty('transform', 'none', 'important');
                    }
                }
            }); 
            
            // Append the button into the chart container wrapper 
            chart.style.position = 'relative'; 
            chart.appendChild(toggleBtn); 
        }); 
    }); 
    
    observer.observe(document.body, { childList: true, subtree: true }); 
});