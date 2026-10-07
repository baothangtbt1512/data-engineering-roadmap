SELECT 
    DATE_TRUNC('month', o.order_date)::DATE AS thang,
    c.region AS khu_vuc,
    p.product_name AS san_pham,
    c.customer_name AS khach_hang,
    SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS doanh_thu
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN customers c    ON o.customer_id = c.customer_id
JOIN products p     ON oi.product_id = p.product_id
WHERE o.status = 'COMPLETED'
GROUP BY 1, 2, 3, 4
ORDER BY thang DESC, doanh_thu DESC;