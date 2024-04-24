import numpy as np
import paddle


class LayerCase(paddle.nn.Layer):
    """
    case名称: t_base
    api简介: 对小于等于2维的Tensor进行数据转置。0维和1维Tensor返回本身
    """

    def __init__(self):
        super(LayerCase, self).__init__()

    def forward(self, input, ):
        """
        forward
        """
        out = paddle.t(input,  )
        return out


def create_tensor_inputs():
    """
    paddle tensor
    """
    inputs = (paddle.to_tensor(-1 + (1 - -1) * np.random.random([7, 4]).astype('float32'), dtype='float32', stop_gradient=False), )
    return inputs


def create_numpy_inputs():
    """
    numpy array
    """
    inputs = (-1 + (1 - -1) * np.random.random([7, 4]).astype('float32'), )
    return inputs

