
(cl:in-package :asdf)

(defsystem "esp32_msgs-msg"
  :depends-on (:roslisp-msg-protocol :roslisp-utils )
  :components ((:file "_package")
    (:file "Esp32Data" :depends-on ("_package_Esp32Data"))
    (:file "_package_Esp32Data" :depends-on ("_package"))
  ))