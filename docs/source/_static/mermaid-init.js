// Initialize Mermaid diagrams
document.addEventListener('DOMContentLoaded', function() {
    if (typeof mermaid !== 'undefined') {
        mermaid.initialize({ 
            startOnLoad: true,
            theme: 'default',
            themeVariables: {
                primaryColor: '#2563eb',
                primaryTextColor: '#fff',
                primaryBorderColor: '#1976d2',
                lineColor: '#5e72e4',
                secondaryColor: '#7c3aed',
                tertiaryColor: '#10b981'
            }
        });
        
        // Re-render mermaid diagrams after theme switch
        const themeButtons = document.querySelectorAll('.theme-switch-button');
        themeButtons.forEach(button => {
            button.addEventListener('click', function() {
                setTimeout(() => {
                    mermaid.run();
                }, 100);
            });
        });
    }
});