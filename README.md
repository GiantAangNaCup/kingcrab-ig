# Kingcrab Frozen · IG carousel อัตโนมัติ

ทุกวันเวลา ~18:47 (เวลาไทย) GitHub จะหยิบโพสต์ถัดไปในโฟลเดอร์ `posts/` แล้วโพสต์ลง Instagram เป็น carousel วันละ 1 โพสต์

- `posts/<วันที่>/01.jpg …` สไลด์ (JPEG 1080×1350) และ `caption.txt` แคปชัน
  ชื่อโฟลเดอร์ใช้กำหนดลำดับเท่านั้น ถ้าเริ่มช้า ระบบจะโพสต์ต่อตามลำดับ ไม่ข้าม
- โพสต์แล้วจะมีไฟล์ `.posted` (วันที่โพสต์ + ลิงก์) อยู่ในโฟลเดอร์นั้น
- `content/*.json` เนื้อหาต้นฉบับ + ลิงก์ภาพประกอบจาก Higgsfield; ทุกครั้งที่แก้ไฟล์นี้ GitHub จะสร้างสไลด์ใหม่ใน `posts/` ให้เอง (workflow Render slides)
- ถ้าคิวหมดหรือโพสต์ไม่สำเร็จ GitHub จะส่งอีเมลแจ้ง

## Secrets ที่ต้องตั้ง (Settings → Secrets and variables → Actions)
- `IG_TOKEN` token ระยะยาวของ Instagram (จากแอปใน Meta for Developers)
- `GH_PAT` (ไม่บังคับ) ใช้ต่ออายุ `IG_TOKEN` อัตโนมัติทุกวันจันทร์ ไม่อย่างนั้น token หมดอายุใน 60 วัน

## สั่งโพสต์เอง / ทดสอบ
Actions → Post to Instagram → Run workflow (ติ๊ก dry run เพื่อดูเฉยๆ ไม่โพสต์จริง)
