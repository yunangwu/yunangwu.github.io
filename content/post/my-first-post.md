---
title: Testing Hugo
date: '2024-05-25'
tags:
  - misc
plotly: true
---

# Text
In a bustling city, amidst towering skyscrapers, lived a forgotten clockmaker named Ezra. His tiny shop, tucked away in an alley, held secrets of intricate timepieces crafted with precision and love. Each tick echoed memories of forgotten moments, each tock whispered dreams of lost souls. Yet, despite the cacophony of life outside, Ezra found solace in the symphony of gears and springs. One stormy night, a stranger stumbled upon his shop, seeking shelter from the tempest. With a warm smile, Ezra invited the weary traveler in, offering tea and tales of time woven into the fabric of their souls.

---

# JS
{{< ball-bouncing >}}

---

# Latex
$$\frac{\partial \mathbf{v}}{\partial t} + (\mathbf{v} \cdot \nabla) \mathbf{v} = -\frac{1}{\rho} \nabla p + \nu \nabla^2 \mathbf{v}$$

---

# Code
### C
```c
void bubbleSort(int arr[], int n) {
    for (int i = 0; i < n - 1; i++)
        for (int j = 0; j < n - i - 1; j++)
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
}
```
### SQL
```SQL
CREATE TABLE Employees (
    EmployeeID INT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Department VARCHAR(50),
    Salary DECIMAL(10, 2)
);

```
### Python
```python
def fibonacci(n):
    fib_sequence = [0, 1]
    for i in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence 
```

---

# Plotly
{{< plotly json="/json/mtbruno.json" height="500px">}}




