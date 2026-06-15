// Auto-generated. Do not edit!

// (in-package esp32_msgs.msg)


"use strict";

const _serializer = _ros_msg_utils.Serialize;
const _arraySerializer = _serializer.Array;
const _deserializer = _ros_msg_utils.Deserialize;
const _arrayDeserializer = _deserializer.Array;
const _finder = _ros_msg_utils.Find;
const _getByteLength = _ros_msg_utils.getByteLength;

//-----------------------------------------------------------

class Esp32Data {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.v1 = null;
      this.v2 = null;
      this.v3 = null;
      this.v4 = null;
      this.v5 = null;
    }
    else {
      if (initObj.hasOwnProperty('v1')) {
        this.v1 = initObj.v1
      }
      else {
        this.v1 = 0;
      }
      if (initObj.hasOwnProperty('v2')) {
        this.v2 = initObj.v2
      }
      else {
        this.v2 = 0;
      }
      if (initObj.hasOwnProperty('v3')) {
        this.v3 = initObj.v3
      }
      else {
        this.v3 = 0;
      }
      if (initObj.hasOwnProperty('v4')) {
        this.v4 = initObj.v4
      }
      else {
        this.v4 = 0;
      }
      if (initObj.hasOwnProperty('v5')) {
        this.v5 = initObj.v5
      }
      else {
        this.v5 = 0;
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type Esp32Data
    // Serialize message field [v1]
    bufferOffset = _serializer.int32(obj.v1, buffer, bufferOffset);
    // Serialize message field [v2]
    bufferOffset = _serializer.int32(obj.v2, buffer, bufferOffset);
    // Serialize message field [v3]
    bufferOffset = _serializer.int32(obj.v3, buffer, bufferOffset);
    // Serialize message field [v4]
    bufferOffset = _serializer.int32(obj.v4, buffer, bufferOffset);
    // Serialize message field [v5]
    bufferOffset = _serializer.int32(obj.v5, buffer, bufferOffset);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type Esp32Data
    let len;
    let data = new Esp32Data(null);
    // Deserialize message field [v1]
    data.v1 = _deserializer.int32(buffer, bufferOffset);
    // Deserialize message field [v2]
    data.v2 = _deserializer.int32(buffer, bufferOffset);
    // Deserialize message field [v3]
    data.v3 = _deserializer.int32(buffer, bufferOffset);
    // Deserialize message field [v4]
    data.v4 = _deserializer.int32(buffer, bufferOffset);
    // Deserialize message field [v5]
    data.v5 = _deserializer.int32(buffer, bufferOffset);
    return data;
  }

  static getMessageSize(object) {
    return 20;
  }

  static datatype() {
    // Returns string type for a message object
    return 'esp32_msgs/Esp32Data';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return 'a281a2c1c2d8004205b58477743bf196';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    int32 v1
    int32 v2
    int32 v3
    int32 v4
    int32 v5
    
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new Esp32Data(null);
    if (msg.v1 !== undefined) {
      resolved.v1 = msg.v1;
    }
    else {
      resolved.v1 = 0
    }

    if (msg.v2 !== undefined) {
      resolved.v2 = msg.v2;
    }
    else {
      resolved.v2 = 0
    }

    if (msg.v3 !== undefined) {
      resolved.v3 = msg.v3;
    }
    else {
      resolved.v3 = 0
    }

    if (msg.v4 !== undefined) {
      resolved.v4 = msg.v4;
    }
    else {
      resolved.v4 = 0
    }

    if (msg.v5 !== undefined) {
      resolved.v5 = msg.v5;
    }
    else {
      resolved.v5 = 0
    }

    return resolved;
    }
};

module.exports = Esp32Data;
