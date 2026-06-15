;; Auto-generated. Do not edit!


(when (boundp 'esp32_msgs::Esp32Data)
  (if (not (find-package "ESP32_MSGS"))
    (make-package "ESP32_MSGS"))
  (shadow 'Esp32Data (find-package "ESP32_MSGS")))
(unless (find-package "ESP32_MSGS::ESP32DATA")
  (make-package "ESP32_MSGS::ESP32DATA"))

(in-package "ROS")
;;//! \htmlinclude Esp32Data.msg.html


(defclass esp32_msgs::Esp32Data
  :super ros::object
  :slots (_v1 _v2 _v3 _v4 _v5 ))

(defmethod esp32_msgs::Esp32Data
  (:init
   (&key
    ((:v1 __v1) 0)
    ((:v2 __v2) 0)
    ((:v3 __v3) 0)
    ((:v4 __v4) 0)
    ((:v5 __v5) 0)
    )
   (send-super :init)
   (setq _v1 (round __v1))
   (setq _v2 (round __v2))
   (setq _v3 (round __v3))
   (setq _v4 (round __v4))
   (setq _v5 (round __v5))
   self)
  (:v1
   (&optional __v1)
   (if __v1 (setq _v1 __v1)) _v1)
  (:v2
   (&optional __v2)
   (if __v2 (setq _v2 __v2)) _v2)
  (:v3
   (&optional __v3)
   (if __v3 (setq _v3 __v3)) _v3)
  (:v4
   (&optional __v4)
   (if __v4 (setq _v4 __v4)) _v4)
  (:v5
   (&optional __v5)
   (if __v5 (setq _v5 __v5)) _v5)
  (:serialization-length
   ()
   (+
    ;; int32 _v1
    4
    ;; int32 _v2
    4
    ;; int32 _v3
    4
    ;; int32 _v4
    4
    ;; int32 _v5
    4
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; int32 _v1
       (write-long _v1 s)
     ;; int32 _v2
       (write-long _v2 s)
     ;; int32 _v3
       (write-long _v3 s)
     ;; int32 _v4
       (write-long _v4 s)
     ;; int32 _v5
       (write-long _v5 s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; int32 _v1
     (setq _v1 (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;; int32 _v2
     (setq _v2 (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;; int32 _v3
     (setq _v3 (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;; int32 _v4
     (setq _v4 (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;; int32 _v5
     (setq _v5 (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;;
   self)
  )

(setf (get esp32_msgs::Esp32Data :md5sum-) "a281a2c1c2d8004205b58477743bf196")
(setf (get esp32_msgs::Esp32Data :datatype-) "esp32_msgs/Esp32Data")
(setf (get esp32_msgs::Esp32Data :definition-)
      "int32 v1
int32 v2
int32 v3
int32 v4
int32 v5

")



(provide :esp32_msgs/Esp32Data "a281a2c1c2d8004205b58477743bf196")


