import numpy as np
import paddle


class LayerCase(paddle.nn.Layer):
    """
    case名称: Pad2D_24
    api简介: 2维pad填充
    """

    def __init__(self):
        super(LayerCase, self).__init__()
        self.func = paddle.nn.Pad2D(padding=[2, 1, 2, 1], mode='replicate', data_format='NHWC', )

    def forward(self, data, ):
        """
        forward
        """
        out = self.func(data, )
        return out


def create_tensor_inputs():
    """
    paddle tensor
    """
    inputs = (paddle.to_tensor(-1 + (1 - -1) * np.random.random([1, 2, 3, 4]).astype('float32'), dtype='float32', stop_gradient=False), )
    return inputs


def create_numpy_inputs():
    """
    numpy array
    """
    inputs = (-1 + (1 - -1) * np.random.random([1, 2, 3, 4]).astype('float32'), )
    return inputs

