# E-learning Management System Project
E-learning Management System Project หรือ SimpleCourse จัดทำขึ้นเพื่อศึกษาการสร้างเว็ปแอพและการ deployment เว็ปแอพของตนเอง  
(โปรเจคนี้มีวัตถุประสงค์เพื่อใช้ในการศึกษา This project made for education purpose.)  

## Integrate Apps
  + [Vercel](https://vercel.com/)
  + [Neon serverless postgres](https://neon.com/)
  + [Supabase S3 storage](https://supabase.com/)

## Libraries
  + [JQuery](https://api.jquery.com/)
  + [Bootstrap5](https://getbootstrap.com/)
  + [Owlcarousel](https://owlcarousel2.github.io/OwlCarousel2/)
  + [Animate.css](https://animate.style/)
  + [Wow.js](https://wowjs.uk/)
  + [Chart.js](https://www.chartjs.org/)
  + [SweetAlert2 (Sweetify)](https://github.com/Atrox/sweetify-django/)

## Install Requirements
  + Python 3.12
  + Django Framework

## Installing
  + git clone https://github.com/PotatoAom/Simple-Elearning-System.git
  + ติดตั้ง Python libraries ที่จำเป็น
  ```
  pip install -r requirements.txt
  ```
  + สร้าง database สำหรับ sqlite3
  ```
  python manage.py migrate
  ```
  + สร้าง superuser สำหรับใช้งาน django admin
  ```
  python manage.py createsuperuser
  ```
  + runserver ในโหมด developer mode
  ```
  python manage.py runserver
  ```

## วัตถุประสงค์
  + เพื่อศึกษาวิธีการใช้งาน Django Framework
  + เพื่อฝึกการเขียนโปรแกรมด้วยภาษา Python
  + ฝึกการออกแบบระบบ Web Applications
  + เพิ่มช่องทางในการศึกษารูปแบบใหม่
  + สามารถนำไปต่อยอดการพัฒนาเว็บแอปพลิเคชั่นต่อไปในอนาคต

## Function ที่ต้องมีในระบบ
+ Admin
  - [x] ใช้ Django Administrator สำหรับ Admin
+ Student
  - [x] ระบบ Authentication
  - [x] ระบบ Profile
  - [x] ระบบ ดู / เข้าห้องเรียนออนไลน์
  - [x] ระบบ ห้องเรียนออนไลน์ 
  - [x] ระบบ Assignments 
  - [x] ระบบ ทำแบบทดสอบ
  - [x] ระบบ ดูคะแนน
+ Teacher
  - [x] ระบบ Authentication
  - [x] ระบบ Profile
  - [x] ระบบ สร้างห้องเรียน
  - [x] ระบบ จัดการห้องเรียน 
  - [x] ระบบ สร้าง Assignments 
  - [x] ระบบ สร้างแบบทดสอบ
  - [x] ระบบ จัดการแบบทดสอบ
  