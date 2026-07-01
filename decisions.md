# retail-sales-dw

## description

This project simulates a fictional retail company called NovaMart — a mid-sized chain selling electronics, clothing, and home goods across multiple store branches. NovaMart's operations team has been tracking sales, inventory, and customer data in a messy spreadsheet system for years. The task is to design and build their first proper data infrastructure: a normalized transactional database that accurately captures their business operations, and then a separate analytical data warehouse that their BI team can query to answer business questions.

## Business Context & Requirements

The BI team has handed you a list of questions they need to answer regularly. Your warehouse must be able to support all of them:

- What are the total sales revenue and units sold per product category per month?
- Which store branches are performing above average compared to others in the same region?
- Who are the top 10% of customers by lifetime value, and what categories do they buy from?
- How has the average order value trended week-over-week over the last year?
- Which products have never been sold in a specific branch?
- What is the sales performance of each sales rep broken down by quarter?

## Phase 1 : OLTP Design

![alt text](images/OLTP_ERD.png)

1. The first decision after creating the `order` table was to split it into `order` and `order_items` because one order could contain many items and to achieve the 3NF.
2. You will notice that there are two columns for price: one in the `order_items` table -> `unit_price`, and another in the `product` table -> `price`, because the table needs to record the instant price the customer bought at, and the price of the product can change later.
3. `branch_id` was added to the `order` table for the performance metrics checked by the analysts and to reduce redundancy. An alternative approach was to put it in the `order_items` table, but it would be redundant as one customer can buy multiple items from the same branch, breaking the 3NF rule.
4. `category` also got its own table to remove redundancy.

## Tech stack choice to deploy phase 1

1. Docker: it's a container service that makes the application portable to be reused on any other machine.
2. PostgreSQL: will be great for OLTP because it supports ACID compliance for transactional integrity. ACID stands for:
    - Atomicity: if two customers try to buy the last item at the same time, the database will not allow it.
    - Consistency: all data follows the same rules and is consistent, like a price can't be below zero.
    - Isolation: when two operations happen at the same time, they should be separated, or rather isolated, to not affect each other.
    - Durability: what if the system shuts down? What happens to the data? It will be safe because it is saved on the hard disk.

## Synthetic data generation 
 - all the data metrics were done by reasonable assumptions under ambiguity because this not a real data set .
 - Customers: ~10,000
 - Products: ~500 -> this to randomaly makes some products statiscally be zero in some branches
 - Regions: 10 this was reasonalbe number of retail chain regions
 - Branches: 30-50 (3-5 per region) -> to answer ranking question in analysis
 - Employees: 15-20 per branch (~500-1000 total), only some appear as sales reps in orders , i assume only those are sales rep. 
 - Orders: spanning ~1 year
