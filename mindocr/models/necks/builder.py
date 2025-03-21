__all__ = ['build_neck']
supported_necks = [
    'FPN',
    'DBFPN',
    'RNNEncoder',
    'Select',
    'Img2Seq',
    'PSEFPN',
    'EASTFPN',
    'MasterEncoder',
    'RSEFPN',
    'YOLOv8Neck',
    'Identity',
    'RPN'
]
from .fpn import DBFPN, EASTFPN, FPN, PSEFPN, RSEFPN
from .identity import Identity
from .img2seq import Img2Seq
from .master_encoder import MasterEncoder
from .rnn import RNNEncoder
from .rpn.rpn import RPN
from .select import Select
from .yolov8_neck import YOLOv8Neck


def build_neck(neck_name, **kwargs):
    """
    Build Neck network.

    Args:
        neck_name (str): the neck name, which shoule be one of the supported_necks.
        kwargs (dict): input args for the neck network

    Return:
        nn.Cell for neck module

    Construct:
        Input: Tensor
        Output: Dict[Tensor]

    Example:
        >>> # build RNNEncoder
        >>> from mindocr.models.necks import build_neck
        >>> config = dict(neck_name='RNNEncoder', in_channels=128, hidden_size=256)
        >>> neck = build_neck(**config)
        >>> print(neck)
    """
    assert neck_name in supported_necks, f'Invalid neck: {neck_name}, Support necks are {supported_necks}'
    neck = eval(neck_name)(**kwargs)
    return neck
