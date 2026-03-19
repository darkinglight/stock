"""计算工具模块"""


def calculate_intrinsic_growth_rate(roe: float, bonus_rate: float, pb: float) -> float:
    """计算企业内在年化增长率
    
    Args:
        roe: 净资产收益率（最近4个季度总和）
        bonus_rate: 分红率
        pb: 市净率
    
    Returns:
        企业内在年化增长率
    """
    if pb <= 0:
        return 0.0
    return roe * (1 - bonus_rate) + roe * bonus_rate / pb


def calculate_quarterly_roe(current_roe: float, previous_roe: float, is_first_quarter: bool) -> float:
    """计算单季度ROE
    
    Args:
        current_roe: 当前季度财报ROE
        previous_roe: 上一季度财报ROE
        is_first_quarter: 是否为第一季度
    
    Returns:
        单季度ROE
    """
    if is_first_quarter:
        return current_roe
    return current_roe - previous_roe


def calculate_trailing_12m_roe(quarterly_roes: list) -> float:
    """计算最近12个月（4个季度）的ROE总和
    
    Args:
        quarterly_roes: 季度ROE列表
    
    Returns:
        最近12个月ROE总和
    """
    return sum(quarterly_roes[-4:]) if len(quarterly_roes) >= 4 else sum(quarterly_roes)


def calculate_debt_to_asset_ratio(total_liabilities: float, total_assets: float) -> float:
    """计算资产负债率
    
    Args:
        total_liabilities: 总负债
        total_assets: 总资产
    
    Returns:
        资产负债率（百分比）
    """
    if total_assets <= 0:
        return 0.0
    return (total_liabilities / total_assets) * 100


def is_debt_ratio_acceptable(debt_ratio: float) -> bool:
    """判断资产负债率是否可接受（不超过70%）
    
    Args:
        debt_ratio: 资产负债率
    
    Returns:
        是否可接受
    """
    return debt_ratio <= 70.0
