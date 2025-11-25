const CLASS_LABELS: Record<string, string> = {
  'plastic_bottle': 'Chai nhựa',
  'plastic_bag': 'Túi nhựa',
  'plastic_box': 'Hộp nhựa',
  'plastic_cup': 'Ly nhựa',
  'plastic_cup_lid': 'Nắp ly nhựa',
  'plastic_cultery': 'Dụng cụ nhựa',
  'plastic_bottle_cap': 'Nắp chai nhựa',
  'plastic': 'Nhựa',
  'plastic_box_container': 'Hộp đựng nhựa',
  'plastic_container': 'Hộp nhựa',
  'plastic_cutlery': 'Dụng cụ nhựa',
  'straw': 'Ống hút',
  'cup': 'Ly',
  'paper': 'Giấy',
  'scrap_paper': 'Giấy vụn',
  'reuseable_paper': 'Giấy tái sử dụng',
  'cardboard': 'Bìa carton',
  'cardboard_box': 'Thùng carton',
  'cardboard_bowl': 'Tô giấy',
  'cardboard_cup': 'Ly giấy',
  'cardboard_plate': 'Dĩa giấy',
  'bottle': 'Chai',
  'glass': 'Thủy tinh',
  'brown-glass': 'Thủy tinh nâu',
  'green-glass': 'Thủy tinh xanh',
  'white-glass': 'Thủy tinh trắng',
  'metal': 'Kim loại',
  'can': 'Lon kim loại',
  'chemical_spray_can': 'Bình xịt hóa chất',
  'chemical_plastic_bottle': 'Chai hóa chất nhựa',
  'chemical_plastic_gallon': 'Can hóa chất',
  'battery': 'Pin',
  'light_bulb': 'Bóng đèn',
  'paint_bucket': 'Thùng sơn',
  'snack_bag': 'Gói snack',
  'plastic_bottle_label': 'Nhãn chai nhựa',
  'stick': 'Que gỗ',
  'trash': 'Rác',
  'garbage': 'Rác',
  'organic': 'Rác hữu cơ',
  'banana': 'Chuối',
  'apple': 'Táo',
  'broccoli': 'Bông cải',
  'carrot': 'Cà rốt',
  'pizza': 'Pizza',
  'donut': 'Bánh donut',
  'cake': 'Bánh kem',
  'sandwich': 'Bánh sandwich',
  'hot dog': 'Bánh hotdog',
  'book': 'Sách',
  'newspaper': 'Báo',
  'magazine': 'Tạp chí',
  'bowl': 'Tô',
  'battery_cell': 'Pin tiểu',
  'biological': 'Rác hữu cơ',
  'clothes': 'Quần áo',
  'shoes': 'Giày dép'
};

const MATERIAL_LABELS: Record<string, string> = {
  plastic: 'Nhựa',
  glass: 'Thủy tinh',
  metal: 'Kim loại',
  paper: 'Giấy',
  cardboard: 'Bìa',
  ceramic: 'Gốm sứ',
  fabric: 'Vải',
  textile: 'Vải',
  organic: 'Hữu cơ'
};

const MATERIAL_KEYWORDS: Array<[string, string]> = [
  ['plastic', 'plastic'],
  ['glass', 'glass'],
  ['metal', 'metal'],
  ['aluminum', 'metal'],
  ['steel', 'metal'],
  ['iron', 'metal'],
  ['can', 'metal'],
  ['tin', 'metal'],
  ['paper', 'paper'],
  ['cardboard', 'cardboard'],
  ['carton', 'cardboard'],
  ['ceramic', 'ceramic'],
  ['clay', 'ceramic'],
  ['cloth', 'fabric'],
  ['fabric', 'fabric'],
  ['textile', 'fabric'],
  ['organic', 'organic'],
];

const toTitleCase = (text: string) =>
  text
    .replace(/[_-]/g, ' ')
    .split(' ')
    .filter(Boolean)
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');

export const formatMaterialName = (material?: string) => {
  if (!material) return '';
  const key = material.toLowerCase();
  return MATERIAL_LABELS[key] || toTitleCase(material);
};

export const getMaterialFromClassName = (className?: string) => {
  if (!className) return '';
  const normalized = className.toLowerCase();
  for (const [keyword, material] of MATERIAL_KEYWORDS) {
    if (normalized.includes(keyword)) {
      return material;
    }
  }
  return '';
};

export const formatDetectionName = (className?: string) => {
  if (!className) return '';
  const normalized = className.toLowerCase();
  if (CLASS_LABELS[normalized]) {
    return CLASS_LABELS[normalized];
  }

  if (normalized.includes('-')) {
    const [base, mat] = normalized.split('-', 2);
    if (CLASS_LABELS[base]) {
      return `${CLASS_LABELS[base]} (${formatMaterialName(mat)})`;
    }
  }

  return toTitleCase(className);
};

