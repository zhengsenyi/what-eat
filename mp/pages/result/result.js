// pages/result/result.js
Page({
  data: {
    result: {
      id: 3,
      name: '冬阴功汤',
      restaurant: '泰香米餐厅',
      rating: 4.9,
      price: 48,
      tags: ['午餐', '晚餐', '预算30-50元'],
      description: '地道泰国风味，酸辣开胃。采用新鲜柠檬叶和朝天椒炮制，汤色红亮，口感层次丰富，是来泰香米必点的招牌菜。',
      review: '酸辣适中，真的很开胃！强烈推荐给喜欢泰国菜的朋友。',
      image: 'https://images.unsplash.com/photo-1562565652-a0d8f0c59eb4?w=800&h=600&fit=crop'
    },
    similarItems: [
      {
        id: 4,
        name: '绿咖喱鸡',
        restaurant: '南洋小馆',
        rating: 4.7,
        price: 42,
        image: 'https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=400&h=300&fit=crop'
      },
      {
        id: 5,
        name: '泰式酸辣虾',
        restaurant: '越苑越南菜',
        rating: 4.6,
        price: 52,
        image: 'https://images.unsplash.com/photo-1559314809-0d155014e29e?w=400&h=300&fit=crop'
      },
      {
        id: 6,
        name: '咖喱蟹',
        restaurant: '泰香米餐厅',
        rating: 4.5,
        price: 68,
        image: 'https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&h=300&fit=crop'
      }
    ],
    isFavorite: false,
    scene: '',
    budget: 0
  },

  onLoad(options) {
    // 获取传递的参数
    if (options.scene) {
      this.setData({ scene: options.scene });
    }
    if (options.budget) {
      this.setData({ budget: parseInt(options.budget) });
    }

    // 检查是否已收藏
    this.checkFavorite();
    
    // 模拟根据参数获取推荐结果
    this.fetchResult();
  },

  // 获取推荐结果
  fetchResult() {
    // 这里可以根据 scene 和 budget 参数从服务器获取推荐
    // 目前使用模拟数据
    const results = [
      {
        id: 1,
        name: '冬阴功汤',
        restaurant: '泰香米餐厅',
        rating: 4.9,
        price: 48,
        tags: ['午餐', '晚餐', '预算30-50元'],
        description: '地道泰国风味，酸辣开胃。采用新鲜柠檬叶和朝天椒炮制，汤色红亮，口感层次丰富。',
        review: '酸辣适中，真的很开胃！',
        image: 'https://images.unsplash.com/photo-1562565652-a0d8f0c59eb4?w=800&h=600&fit=crop'
      },
      {
        id: 2,
        name: '麻婆豆腐',
        restaurant: '川味小馆',
        rating: 4.7,
        price: 32,
        tags: ['午餐', '晚餐', '预算20-40元'],
        description: '正宗川味，麻辣鲜香。选用嫩豆腐，配以牛肉末和郫县豆瓣酱，口感细腻。',
        review: '麻辣够味，下饭神器！',
        image: 'https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?w=800&h=600&fit=crop'
      },
      {
        id: 3,
        name: '豚骨拉面',
        restaurant: '一兰拉面',
        rating: 4.8,
        price: 45,
        tags: ['午餐', '晚餐', '预算40-60元'],
        description: '浓郁豚骨汤底，配以叉烧、溏心蛋和葱花，面条劲道有嚼劲。',
        review: '汤底超级浓郁，面条很有嚼劲！',
        image: 'https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=800&h=600&fit=crop'
      }
    ];

    // 随机选择一个结果
    const randomIndex = Math.floor(Math.random() * results.length);
    this.setData({
      result: results[randomIndex]
    });
  },

  // 检查是否已收藏
  checkFavorite() {
    const favorites = wx.getStorageSync('favorites') || [];
    const isFavorite = favorites.some(item => item.id === this.data.result.id);
    this.setData({ isFavorite });
  },

  // 返回上一页
  goBack() {
    wx.navigateBack();
  },

  // 重新抽选
  reRoll() {
    wx.vibrateShort({ type: 'medium' });
    
    wx.showLoading({
      title: '重新抽选中...',
      mask: true
    });

    setTimeout(() => {
      this.fetchResult();
      this.checkFavorite();
      wx.hideLoading();
      
      wx.showToast({
        title: '换了一个推荐',
        icon: 'none'
      });
    }, 800);
  },

  // 切换收藏状态
  toggleFavorite() {
    wx.vibrateShort({ type: 'light' });
    
    const favorites = wx.getStorageSync('favorites') || [];
    const { result, isFavorite } = this.data;

    if (isFavorite) {
      // 取消收藏
      const newFavorites = favorites.filter(item => item.id !== result.id);
      wx.setStorageSync('favorites', newFavorites);
      
      this.setData({ isFavorite: false });
      
      wx.showToast({
        title: '已取消收藏',
        icon: 'none'
      });
    } else {
      // 添加收藏
      favorites.push({
        id: result.id,
        name: result.name,
        restaurant: result.restaurant,
        rating: result.rating,
        price: result.price,
        image: result.image,
        addTime: new Date().toISOString()
      });
      wx.setStorageSync('favorites', favorites);
      
      this.setData({ isFavorite: true });
      
      wx.showToast({
        title: '已添加到收藏',
        icon: 'success'
      });
    }

    // 更新统计
    const stats = wx.getStorageSync('userStats') || { favoriteCount: 0, totalDraws: 0 };
    stats.favoriteCount = favorites.length;
    wx.setStorageSync('userStats', stats);
  },

  // 打开导航
  openNavigation() {
    wx.showActionSheet({
      itemList: ['高德地图', '百度地图', '腾讯地图'],
      success: (res) => {
        wx.showToast({
          title: '正在打开导航...',
          icon: 'none'
        });
        // 这里可以调用对应的地图API
      }
    });
  },

  // 分享
  onShare() {
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    });
  },

  // 选择相似推荐
  selectSimilar(e) {
    const item = e.currentTarget.dataset.item;
    
    wx.vibrateShort({ type: 'light' });
    
    // 更新当前结果
    this.setData({
      result: {
        ...item,
        tags: ['推荐', '相似菜品'],
        description: '这是一道美味的菜品，值得一试！',
        review: '味道很不错，推荐尝试！'
      }
    });

    // 检查新结果的收藏状态
    this.checkFavorite();

    // 滚动到顶部
    wx.pageScrollTo({
      scrollTop: 0,
      duration: 300
    });
  },

  // 确认选择
  confirmChoice() {
    wx.vibrateShort({ type: 'medium' });
    
    const { result } = this.data;
    
    // 保存到历史记录
    const history = wx.getStorageSync('drawHistory') || [];
    const newHistory = [
      {
        id: result.id,
        name: result.name,
        restaurant: result.restaurant,
        rating: result.rating,
        price: result.price,
        image: result.image,
        drawTime: new Date().toISOString()
      },
      ...history.filter(item => item.id !== result.id)
    ].slice(0, 20); // 最多保存20条
    
    wx.setStorageSync('drawHistory', newHistory);

    wx.showModal({
      title: '选择成功！',
      content: `已选择「${result.name}」\n祝您用餐愉快！🎉`,
      showCancel: false,
      confirmText: '好的',
      confirmColor: '#84cc16',
      success: () => {
        wx.navigateBack();
      }
    });
  },

  // 分享给朋友
  onShareAppMessage() {
    const { result } = this.data;
    return {
      title: `我在吃啥盲盒抽到了「${result.name}」，你也来试试！`,
      path: '/pages/login/login',
      imageUrl: result.image
    };
  },

  // 分享到朋友圈
  onShareTimeline() {
    const { result } = this.data;
    return {
      title: `吃啥盲盒推荐：${result.name} - ${result.restaurant}`,
      query: ''
    };
  }
});
