WITH monthly_revenue AS (
    SELECT 
        DATE_TRUNC('month', o.order_date)::DATE AS sales_month,
        ROUND(SUM(oi.quantity * oi.unit_price * (1 - COALESCE(oi.discount, 0))), 2) AS current_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status = 'COMPLETED'
    GROUP BY 1
)
SELECT 
    sales_month,
    current_revenue,
    
    -- 1. Doanh thu tích lũy qua các tháng (Running Total)
    SUM(current_revenue) OVER (
        ORDER BY sales_month
    ) AS running_total_revenue,
    
    -- 2. Doanh thu của tháng liền trước
    LAG(current_revenue, 1) OVER (
        ORDER BY sales_month
    ) AS prev_month_revenue,
    
    -- 3. Chênh lệch doanh thu tuyệt đối
    ROUND(
        current_revenue - LAG(current_revenue, 1) OVER (ORDER BY sales_month), 
        2
    ) AS revenue_diff,
    
    -- 4. % Tăng trưởng so với tháng trước (MoM Growth %)
    ROUND(
        ((current_revenue - LAG(current_revenue, 1) OVER (ORDER BY sales_month)) 
        / NULLIF(LAG(current_revenue, 1) OVER (ORDER BY sales_month), 0)) * 100, 
        2
    ) AS mom_growth_pct

FROM monthly_revenue
ORDER BY sales_month;