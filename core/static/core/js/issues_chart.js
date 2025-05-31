document.addEventListener('DOMContentLoaded', function () {
    const chartEl = document.getElementById('issueChart');
    if (!chartEl) return;

    const chartDataEl = document.getElementById('chart-data');
    const keywordMessagesEl = document.getElementById('keyword-messages');

    if (!chartDataEl || !keywordMessagesEl) return;

    const chartData = JSON.parse(chartDataEl.textContent);
    const keywordMessages = JSON.parse(keywordMessagesEl.textContent);

    const labels = chartData.labels;
    const data = chartData.data;

    const max = Math.max(...data);
    const colors = data.map(count => {
        const ratio = count / max;
        if (ratio >= 0.8) return '#dc3545';  // Red
        if (ratio >= 0.5) return '#fd7e14';  // Orange
        return '#198754';                   // Green
    });

    const chart = new Chart(chartEl, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Keyword Frequency',
                data: data,
                backgroundColor: colors,
                borderColor: '#000',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            onClick: function (e) {
                const points = chart.getElementsAtEventForMode(e, 'nearest', { intersect: true }, true);
                if (points.length) {
                    const index = points[0].index;
                    const keyword = labels[index];
                    const messages = keywordMessages[keyword] || [];

                    document.getElementById('modalKeyword').textContent = keyword;
                    document.getElementById('modalMessages').innerHTML = messages.map(msg => `<p>${msg}</p>`).join('') || '<p>No messages found.</p>';

                    new bootstrap.Modal(document.getElementById('messageModal')).show();
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    },
                    title: {
                        display: true,
                        text: 'Number of Reports'
                    }
                }
            }
        }
    });
});
