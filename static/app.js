document.addEventListener('DOMContentLoaded', () => {
    const setupOverlay = document.getElementById('setupOverlay');
    const appContainer = document.getElementById('appContainer');
    const setupForm = document.getElementById('setupForm');
    const btnGenerate = document.getElementById('btnGenerate');
    const btnReconfigure = document.getElementById('btnReconfigure');

    // 平台主色 —— CF 蓝 / LeetCode 黄 / AtCoder 绿
    const THEME = {
        Codeforces: '#4A90D9',
        LeetCode: '#F5A623',
        AtCoder: '#4CAF50'
    };

    // 尝试从 localStorage 恢复上次的配置
    const saved = localStorage.getItem('oj_dashboard_config');
    if (saved) {
        try {
            const cfg = JSON.parse(saved);
            document.getElementById('cfInput').value = cfg.cf || '';
            document.getElementById('lcInput').value = cfg.lc || '';
            document.getElementById('lcSite').value = cfg.lc_site || 'cn';
            document.getElementById('acInput').value = cfg.ac || '';
        } catch (_) {}
    }

    // 表单提交
    setupForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const cf = document.getElementById('cfInput').value.trim();
        const lc = document.getElementById('lcInput').value.trim();
        const lc_site = document.getElementById('lcSite').value;
        const ac = document.getElementById('acInput').value.trim();

        if (!cf && !lc && !ac) {
            alert('请至少填写一个平台的用户名！');
            return;
        }

        localStorage.setItem('oj_dashboard_config', JSON.stringify({ cf, lc, lc_site, ac }));

        setupOverlay.style.display = 'none';
        appContainer.style.display = 'block';
        fetchData({ cf, lc, lc_site, ac });
    });

    // 重新配置按钮
    btnReconfigure.addEventListener('click', () => {
        appContainer.style.display = 'none';
        setupOverlay.style.display = 'flex';
        document.getElementById('dashboard').style.display = 'none';
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error').style.display = 'none';
    });

    async function fetchData(params) {
        const loadingEl = document.getElementById('loading');
        const dashboardEl = document.getElementById('dashboard');
        const errorEl = document.getElementById('error');

        loadingEl.style.display = 'block';
        dashboardEl.style.display = 'none';
        errorEl.style.display = 'none';

        btnGenerate.disabled = true;
        btnGenerate.querySelector('.btn-text').textContent = '加载中...';
        btnGenerate.querySelector('.btn-loader').style.display = 'inline-block';

        try {
            const query = new URLSearchParams();
            if (params.cf) query.set('cf', params.cf);
            if (params.lc) query.set('lc', params.lc);
            if (params.lc_site) query.set('lc_site', params.lc_site);
            if (params.ac) query.set('ac', params.ac);

            const response = await fetch(`/api/data?${query.toString()}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            const validPlatforms = data.platforms.filter(p => ['Codeforces', 'LeetCode', 'AtCoder'].includes(p.name));

            loadingEl.style.display = 'none';
            dashboardEl.style.display = 'flex';

            document.getElementById('totalSolvedCount').innerText = data.total_solved.toLocaleString();

            let totalSubmissions = 0;
            for (const count of Object.values(data.heatmap)) {
                totalSubmissions += count;
            }
            document.getElementById('totalSubsCounter').innerText = `${totalSubmissions.toLocaleString()} Submissions`;

            renderTable(validPlatforms);
            renderPieChart(validPlatforms);
            renderSubmissionsHeatmap(data.heatmap);
            renderDifficultyHeatmap(data.difficulty_heatmap);

        } catch (e) {
            loadingEl.style.display = 'none';
            errorEl.style.display = 'block';
            errorEl.innerText = `Error: ${e.message}`;
        } finally {
            btnGenerate.disabled = false;
            btnGenerate.querySelector('.btn-text').textContent = '生成仪表盘';
            btnGenerate.querySelector('.btn-loader').style.display = 'none';
        }
    }

    function renderTable(platforms) {
        const tbody = document.querySelector('#platformsTable tbody');
        tbody.innerHTML = '';

        platforms.forEach(p => {
            const row = document.createElement('tr');
            const color = THEME[p.name] || '#888';
            if (p.error) {
                row.innerHTML = `
                    <td><span class="platform-badge"><span class="platform-dot" style="background:${color}"></span>${p.name}</span></td>
                    <td style="color:red" title="${p.error}">Error</td>`;
            } else {
                row.innerHTML = `
                    <td><span class="platform-badge"><span class="platform-dot" style="background:${color}"></span>${p.name}</span></td>
                    <td><strong>${p.solved}</strong></td>`;
            }
            tbody.appendChild(row);
        });
    }

    function renderPieChart(platforms) {
        const chartDom = document.getElementById('pieChart');
        const myChart = echarts.init(chartDom);

        const validData = platforms.filter(p => !p.error && p.solved > 0).map(p => ({
            value: p.solved,
            name: p.name,
            itemStyle: { color: THEME[p.name] }
        }));

        const option = {
            tooltip: {
                trigger: 'item',
                formatter: '{b}: {c} ({d}%)'
            },
            legend: {
                bottom: '0%',
                left: 'center'
            },
            series: [
                {
                    name: 'Solved',
                    type: 'pie',
                    radius: '60%',
                    center: ['50%', '45%'],
                    data: validData,
                    label: {
                        show: true,
                        formatter: '{b}: {c}',
                        fontSize: 12
                    },
                    labelLine: {
                        show: true,
                        length: 15,
                        length2: 10
                    }
                }
            ]
        };
        myChart.setOption(option);
        window.addEventListener('resize', () => myChart.resize());
    }

    // 通用的日历基础配置
    const getBaseCalendarOption = (yearStart, yearEnd, dataArr, tooltipFormatter, visualMapObj) => {
        return {
            tooltip: {
                position: 'top',
                formatter: tooltipFormatter,
                backgroundColor: '#333',
                borderColor: '#333',
                textStyle: { color: '#fff', fontSize: 12 }
            },
            visualMap: visualMapObj,
            calendar: [
                {
                    range: [yearStart, yearEnd],
                    cellSize: [13, 13],
                    right: 5,
                    left: 35,
                    top: 20,
                    bottom: 10,
                    itemStyle: {
                        color: '#ebedf0',
                        borderWidth: 2,
                        borderColor: '#fff',
                        borderRadius: 0
                    },
                    splitLine: { show: false },
                    yearLabel: { show: false },
                    dayLabel: {
                        firstDay: 1,
                        nameMap: ['S', 'M', 'T', 'W', 'T', 'F', 'S'],
                        color: '#767676',
                        fontSize: 10
                    },
                    monthLabel: {
                        nameMap: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                        color: '#767676',
                        fontSize: 11
                    }
                }
            ],
            series: [
                {
                    type: 'heatmap',
                    coordinateSystem: 'calendar',
                    data: dataArr
                }
            ]
        };
    };

    function renderSubmissionsHeatmap(heatmapData) {
        const chartDom = document.getElementById('heatmapChart');
        const myChart = echarts.init(chartDom);

        const graphData = [];
        for (const [date, count] of Object.entries(heatmapData)) {
            graphData.push([date, count]);
        }

        const today = new Date();
        const lastYear = new Date();
        lastYear.setFullYear(today.getFullYear() - 1);

        const rangeStart = echarts.format.formatTime('yyyy-MM-dd', lastYear);
        const rangeEnd = echarts.format.formatTime('yyyy-MM-dd', today);

        const visualMap = {
            min: 0,
            max: 10,
            calculable: false,
            orient: 'horizontal',
            show: false,
            inRange: {
                color: ['#ebedf0', '#c6e48b', '#7bc96f', '#239a3b', '#196127']
            }
        };

        const tooltipStr = function (p) {
            const format = echarts.format.formatTime('yyyy-MM-dd', p.data[0]);
            return `${p.data[1]} submissions on ${format}`;
        };

        const option = getBaseCalendarOption(rangeStart, rangeEnd, graphData, tooltipStr, visualMap);
        myChart.setOption(option);
        window.addEventListener('resize', () => myChart.resize());
    }

    function renderDifficultyHeatmap(difficultyMap) {
        const chartDom = document.getElementById('difficultyHeatmapChart');
        const myChart = echarts.init(chartDom);

        const graphData = [];
        for (const [date, rating] of Object.entries(difficultyMap)) {
            if (rating > 0) {
                graphData.push([date, rating]);
            }
        }

        const today = new Date();
        const lastYear = new Date();
        lastYear.setFullYear(today.getFullYear() - 1);

        const rangeStart = echarts.format.formatTime('yyyy-MM-dd', lastYear);
        const rangeEnd = echarts.format.formatTime('yyyy-MM-dd', today);

        const visualMap = {
            type: 'piecewise',
            show: false,
            pieces: [
                { min: 2400, color: '#FF7777' },
                { min: 2300, max: 2399, color: '#FFBB55' },
                { min: 2100, max: 2299, color: '#FFCC88' },
                { min: 1900, max: 2099, color: '#FF88FF' },
                { min: 1600, max: 1899, color: '#AAAAFF' },
                { min: 1400, max: 1599, color: '#77DDBB' },
                { min: 1200, max: 1399, color: '#77FF77' },
                { min: 1, max: 1199, color: '#CCCCCC' }
            ]
        };

        const tooltipStr = function (p) {
            const format = echarts.format.formatTime('yyyy-MM-dd', p.data[0]);
            return `Max Rating ${p.data[1]} on ${format}`;
        };

        const option = getBaseCalendarOption(rangeStart, rangeEnd, graphData, tooltipStr, visualMap);
        myChart.setOption(option);
        window.addEventListener('resize', () => myChart.resize());
    }
});
