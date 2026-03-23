/**
 * Mock 数据
 * 模拟后端接口返回的页面配置
 */

/**
 * Section 类型枚举
 */
export const SectionType = {
  QUICK_ENTRY: 1,
  BANNER: 2,
  PRODUCT_LIST: 3,
}

/**
 * 获取 Mock 首页数据
 * @returns {Object} 页面配置数据
 */
export const getMockPageData = () => {
  return {
    systemSet: 1,
    homePageSchemaList: [
      // 1. 快捷入口
      {
        sectionType: SectionType.QUICK_ENTRY,
        sectionId: 'quick-entry-001',
        sectionName: '快捷入口',
        enableComSetting: 1,
        sectionDetailVoList: [
          {
            id: 1,
            name: '超市',
            iconUrl: 'https://fastly.jsdelivr.net/npm/@vant/assets/icon-1.png',
            url: '/supermarket',
          },
          {
            id: 2,
            name: '优惠券',
            iconUrl: 'https://fastly.jsdelivr.net/npm/@vant/assets/icon-2.png',
            url: '/coupons',
            badge: '新',
          },
          {
            id: 3,
            name: '签到',
            iconUrl: 'https://fastly.jsdelivr.net/npm/@vant/assets/icon-3.png',
            url: '/checkin',
          },
          {
            id: 4,
            name: '充值',
            iconUrl: 'https://fastly.jsdelivr.net/npm/@vant/assets/icon-4.png',
            url: '/recharge',
          },
          {
            id: 5,
            name: '拼团',
            iconUrl: 'https://fastly.jsdelivr.net/npm/@vant/assets/icon-5.png',
            url: '/group-buy',
            badge: '热',
          },
          {
            id: 6,
            name: '秒杀',
            iconUrl: 'https://fastly.jsdelivr.net/npm/@vant/assets/icon-6.png',
            url: '/flash-sale',
          },
          {
            id: 7,
            name: '会员',
            iconUrl: 'https://fastly.jsdelivr.net/npm/@vant/assets/icon-7.png',
            url: '/vip',
          },
          {
            id: 8,
            name: '积分',
            iconUrl: 'https://fastly.jsdelivr.net/npm/@vant/assets/icon-8.png',
            url: '/points',
          },
          {
            id: 9,
            name: '客服',
            iconUrl: 'https://fastly.jsdelivr.net/npm/@vant/assets/icon-9.png',
            url: '/customer-service',
          },
          {
            id: 10,
            name: '更多',
            iconUrl: 'https://fastly.jsdelivr.net/npm/@vant/assets/icon-10.png',
            url: '/more',
          },
        ],
      },

      // 2. 轮播图
      {
        sectionType: SectionType.BANNER,
        sectionId: 'banner-001',
        sectionName: '',
        enableComSetting: 1,
        config: {
          autoplay: 3000,
          showIndicators: true,
        },
        sectionDetailVoList: [
          {
            id: 'banner-1',
            imageUrl: 'https://picsum.photos/800/450?random=1',
            url: '/activity/1',
            title: '双十一大促',
          },
          {
            id: 'banner-2',
            imageUrl: 'https://picsum.photos/800/450?random=2',
            url: '/activity/2',
            title: '新人专享',
          },
          {
            id: 'banner-3',
            imageUrl: 'https://picsum.photos/800/450?random=3',
            url: '/activity/3',
            title: '限时秒杀',
          },
        ],
      },

      // 3. 商品列表
      {
        sectionType: SectionType.PRODUCT_LIST,
        sectionId: 'product-list-001',
        sectionName: '热门推荐',
        enableComSetting: 1,
        config: {
          columns: 2,
          moreUrl: '/products',
        },
        sectionDetailVoList: [
          {
            id: 'p1',
            name: 'Apple iPhone 15 Pro Max 256GB 原色钛金属',
            image: 'https://picsum.photos/400/400?random=10',
            price: 9999,
            originalPrice: 10999,
            sales: 8653,
            tags: ['自营', '包邮'],
          },
          {
            id: 'p2',
            name: '华为 Mate 60 Pro 12GB+512GB 雅丹黑',
            image: 'https://picsum.photos/400/400?random=11',
            price: 6999,
            originalPrice: 7999,
            sales: 12580,
            tags: ['新品'],
          },
          {
            id: 'p3',
            name: '小米14 Ultra 徕卡影像 16GB+512GB',
            image: 'https://picsum.photos/400/400?random=12',
            price: 5999,
            sales: 5621,
            tags: ['热销'],
          },
          {
            id: 'p4',
            name: 'OPPO Find X7 Ultra 16GB+256GB',
            image: 'https://picsum.photos/400/400?random=13',
            price: 5499,
            originalPrice: 5999,
            sales: 3289,
          },
          {
            id: 'p5',
            name: 'vivo X100 Pro 天玑9300 16GB+512GB',
            image: 'https://picsum.photos/400/400?random=14',
            price: 4999,
            sales: 4125,
            tags: ['爆款'],
          },
          {
            id: 'p6',
            name: '三星 Galaxy S24 Ultra 12GB+256GB',
            image: 'https://picsum.photos/400/400?random=15',
            price: 8999,
            originalPrice: 9999,
            sales: 2156,
            tags: ['自营'],
          },
        ],
      },
    ],
  }
}

/**
 * 获取 Mock 数据（带延迟）
 * @param {number} delay 延迟时间（毫秒）
 * @returns {Promise<Object>} 页面配置数据
 */
export const getMockPageDataWithDelay = (delay = 500) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(getMockPageData())
    }, delay)
  })
}
