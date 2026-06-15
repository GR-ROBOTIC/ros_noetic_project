; Auto-generated. Do not edit!


(cl:in-package esp32_msgs-msg)


;//! \htmlinclude Esp32Data.msg.html

(cl:defclass <Esp32Data> (roslisp-msg-protocol:ros-message)
  ((v1
    :reader v1
    :initarg :v1
    :type cl:integer
    :initform 0)
   (v2
    :reader v2
    :initarg :v2
    :type cl:integer
    :initform 0)
   (v3
    :reader v3
    :initarg :v3
    :type cl:integer
    :initform 0)
   (v4
    :reader v4
    :initarg :v4
    :type cl:integer
    :initform 0)
   (v5
    :reader v5
    :initarg :v5
    :type cl:integer
    :initform 0))
)

(cl:defclass Esp32Data (<Esp32Data>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <Esp32Data>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'Esp32Data)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name esp32_msgs-msg:<Esp32Data> is deprecated: use esp32_msgs-msg:Esp32Data instead.")))

(cl:ensure-generic-function 'v1-val :lambda-list '(m))
(cl:defmethod v1-val ((m <Esp32Data>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader esp32_msgs-msg:v1-val is deprecated.  Use esp32_msgs-msg:v1 instead.")
  (v1 m))

(cl:ensure-generic-function 'v2-val :lambda-list '(m))
(cl:defmethod v2-val ((m <Esp32Data>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader esp32_msgs-msg:v2-val is deprecated.  Use esp32_msgs-msg:v2 instead.")
  (v2 m))

(cl:ensure-generic-function 'v3-val :lambda-list '(m))
(cl:defmethod v3-val ((m <Esp32Data>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader esp32_msgs-msg:v3-val is deprecated.  Use esp32_msgs-msg:v3 instead.")
  (v3 m))

(cl:ensure-generic-function 'v4-val :lambda-list '(m))
(cl:defmethod v4-val ((m <Esp32Data>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader esp32_msgs-msg:v4-val is deprecated.  Use esp32_msgs-msg:v4 instead.")
  (v4 m))

(cl:ensure-generic-function 'v5-val :lambda-list '(m))
(cl:defmethod v5-val ((m <Esp32Data>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader esp32_msgs-msg:v5-val is deprecated.  Use esp32_msgs-msg:v5 instead.")
  (v5 m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <Esp32Data>) ostream)
  "Serializes a message object of type '<Esp32Data>"
  (cl:let* ((signed (cl:slot-value msg 'v1)) (unsigned (cl:if (cl:< signed 0) (cl:+ signed 4294967296) signed)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) unsigned) ostream)
    )
  (cl:let* ((signed (cl:slot-value msg 'v2)) (unsigned (cl:if (cl:< signed 0) (cl:+ signed 4294967296) signed)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) unsigned) ostream)
    )
  (cl:let* ((signed (cl:slot-value msg 'v3)) (unsigned (cl:if (cl:< signed 0) (cl:+ signed 4294967296) signed)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) unsigned) ostream)
    )
  (cl:let* ((signed (cl:slot-value msg 'v4)) (unsigned (cl:if (cl:< signed 0) (cl:+ signed 4294967296) signed)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) unsigned) ostream)
    )
  (cl:let* ((signed (cl:slot-value msg 'v5)) (unsigned (cl:if (cl:< signed 0) (cl:+ signed 4294967296) signed)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) unsigned) ostream)
    )
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <Esp32Data>) istream)
  "Deserializes a message object of type '<Esp32Data>"
    (cl:let ((unsigned 0))
      (cl:setf (cl:ldb (cl:byte 8 0) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) unsigned) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'v1) (cl:if (cl:< unsigned 2147483648) unsigned (cl:- unsigned 4294967296))))
    (cl:let ((unsigned 0))
      (cl:setf (cl:ldb (cl:byte 8 0) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) unsigned) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'v2) (cl:if (cl:< unsigned 2147483648) unsigned (cl:- unsigned 4294967296))))
    (cl:let ((unsigned 0))
      (cl:setf (cl:ldb (cl:byte 8 0) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) unsigned) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'v3) (cl:if (cl:< unsigned 2147483648) unsigned (cl:- unsigned 4294967296))))
    (cl:let ((unsigned 0))
      (cl:setf (cl:ldb (cl:byte 8 0) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) unsigned) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'v4) (cl:if (cl:< unsigned 2147483648) unsigned (cl:- unsigned 4294967296))))
    (cl:let ((unsigned 0))
      (cl:setf (cl:ldb (cl:byte 8 0) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) unsigned) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'v5) (cl:if (cl:< unsigned 2147483648) unsigned (cl:- unsigned 4294967296))))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<Esp32Data>)))
  "Returns string type for a message object of type '<Esp32Data>"
  "esp32_msgs/Esp32Data")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'Esp32Data)))
  "Returns string type for a message object of type 'Esp32Data"
  "esp32_msgs/Esp32Data")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<Esp32Data>)))
  "Returns md5sum for a message object of type '<Esp32Data>"
  "a281a2c1c2d8004205b58477743bf196")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'Esp32Data)))
  "Returns md5sum for a message object of type 'Esp32Data"
  "a281a2c1c2d8004205b58477743bf196")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<Esp32Data>)))
  "Returns full string definition for message of type '<Esp32Data>"
  (cl:format cl:nil "int32 v1~%int32 v2~%int32 v3~%int32 v4~%int32 v5~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'Esp32Data)))
  "Returns full string definition for message of type 'Esp32Data"
  (cl:format cl:nil "int32 v1~%int32 v2~%int32 v3~%int32 v4~%int32 v5~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <Esp32Data>))
  (cl:+ 0
     4
     4
     4
     4
     4
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <Esp32Data>))
  "Converts a ROS message object to a list"
  (cl:list 'Esp32Data
    (cl:cons ':v1 (v1 msg))
    (cl:cons ':v2 (v2 msg))
    (cl:cons ':v3 (v3 msg))
    (cl:cons ':v4 (v4 msg))
    (cl:cons ':v5 (v5 msg))
))
