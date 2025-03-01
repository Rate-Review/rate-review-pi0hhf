import { FC, useRef, useEffect } from 'react';
import Chart from 'chart.js/auto'; // chart.js v4.0.0+

interface PieChartProps {
  data: {
    labels: string[];
    datasets: [
      {
        data: number[];
        backgroundColor?: string[];
        borderColor?: string[];
        borderWidth?: number;
        hoverBackgroundColor?: string[];
        hoverBorderColor?: string[];
      }
    ];
  };
  options?: any;
  height?: number;
  donut?: boolean;
  cutoutPercentage?: number;
  title?: string;
  tooltip?: boolean;
  animation?: boolean;
  legend?: boolean | { position?: 'top' | 'bottom' | 'left' | 'right' };
  className?: string;
}

/**
 * A reusable pie/donut chart component using Chart.js
 * 
 * @param {PieChartProps} props - The component props
 * @returns {JSX.Element} - The rendered chart component
 */
const PieChart: FC<PieChartProps> = (props) => {
  // Create refs for canvas element and chart instance
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const chartRef = useRef<Chart | null>(null);

  // Destructure props with default values
  const {
    data,
    options = {},
    height = 300,
    donut = false,
    cutoutPercentage = 50,
    title,
    tooltip = true,
    animation = true,
    legend = true,
    className
  } = props;

  useEffect(() => {
    if (!canvasRef.current || !data) return;

    // Default colors if not provided
    const defaultColors = [
      '#2C5282', // primary - deep blue
      '#38A169', // secondary - green
      '#DD6B20', // accent - orange
      '#718096', // neutral - slate
      '#3182CE', // info - blue
      '#805AD5', // purple
      '#D53F8C', // pink
      '#ED8936', // orange
      '#48BB78', // green
      '#4299E1', // blue
      '#A0AEC0', // gray
      '#F56565', // red
    ];

    // Apply default colors if not provided
    if (data.datasets[0] && !data.datasets[0].backgroundColor) {
      data.datasets[0].backgroundColor = data.labels.map(
        (_, i) => defaultColors[i % defaultColors.length]
      );
    }

    // Create chart configuration
    const chartConfig = {
      type: donut ? 'doughnut' : 'pie',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: title
            ? {
                display: true,
                text: title,
                font: {
                  size: 16,
                  weight: 'bold',
                },
                padding: {
                  top: 10,
                  bottom: 20,
                },
              }
            : undefined,
          tooltip: {
            enabled: tooltip,
            callbacks: {
              label: function(context: any) {
                const label = context.label || '';
                const value = context.raw || 0;
                const total = context.chart.data.datasets[0].data.reduce(
                  (sum: number, val: number) => sum + val, 
                  0
                );
                const percentage = Math.round((value / total) * 100);
                return `${label}: ${value} (${percentage}%)`;
              }
            }
          },
          legend: typeof legend === 'boolean'
            ? { display: legend }
            : {
                display: true,
                position: legend?.position || 'top',
              },
        },
        // Set cutout percentage for donut chart
        cutout: donut ? `${cutoutPercentage}%` : undefined,
        animation: animation 
          ? {
              animateRotate: true,
              animateScale: true,
              duration: 1000,
            }
          : false,
      },
    };

    // Merge with custom options
    const mergedConfig = {
      ...chartConfig,
      options: {
        ...chartConfig.options,
        ...options,
        // Ensure plugins options are merged correctly
        plugins: {
          ...chartConfig.options.plugins,
          ...(options?.plugins || {}),
        },
      },
    };

    // Create chart instance
    const ctx = canvasRef.current.getContext('2d');
    if (ctx) {
      // Destroy existing chart instance if it exists
      if (chartRef.current) {
        chartRef.current.destroy();
      }
      
      // Create new chart instance
      chartRef.current = new Chart(ctx, mergedConfig);
    }

    // Handle window resize for responsiveness
    const handleResize = () => {
      if (chartRef.current) {
        chartRef.current.resize();
      }
    };

    window.addEventListener('resize', handleResize);

    // Cleanup function
    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }
    };
  }, [data, options, donut, cutoutPercentage, title, tooltip, animation, legend]);

  return (
    <canvas 
      ref={canvasRef} 
      height={height} 
      className={className}
      aria-label={title || "Pie Chart"}
      role="img"
    />
  );
};

export default PieChart;