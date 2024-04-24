import numpy as np
import paddle


class LayerCase(paddle.nn.Layer):
    """
    case名称: is_empty_0
    api简介: 测试变量是否为空
    """

    def __init__(self):
        super(LayerCase, self).__init__()

    def forward(self, x, ):
        """
        forward
        """
        out = paddle.is_empty(x,  )
        return out


def create_tensor_inputs():
    """
    paddle tensor
    """
    inputs = ()
    return inputs


def create_numpy_inputs():
    """
    numpy array
    """
    inputs = (paddle.to_tensor([], dtype='float32', stop_gradient=False), )
    return inputs

