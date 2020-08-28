from flask import jsonify
import uuid
import logging
import decimal

def logger(name):
    """
    Instantiate the logger component
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
    ch.setFormatter(formatter)
    return logger

def error(message):
    """
    Error response, in case of validation issues
    """
    ref_id = uuid.uuid4()
    logger("efergy").error("{} - {}".format(str(ref_id), message))
    
    return jsonify({
        "Error":message,
        'Reference': ref_id
    }), 400

def not_found():
    return jsonify({
        "Error":"Not found"
    }), 404

def decimal_to_digit_coverter(items):
    decimal_int_cast = lambda i: int(i) if abs(i) % 1 > 0 else float(i)
    for key,value in enumerate(items):
        if isinstance(items[value], decimal.Decimal):
            items[value] = decimal_int_cast(items[value])
    return items