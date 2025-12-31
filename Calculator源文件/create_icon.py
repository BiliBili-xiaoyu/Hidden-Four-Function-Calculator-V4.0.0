# create_icon.py - 自动生成计算器图标
from PIL import Image, ImageDraw, ImageFont
import os

def create_calculator_icon():
    """创建计算器图标"""
    print("正在生成计算器图标...")
    
    # 图标尺寸（ICO文件需要多种尺寸）
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    # 创建不同尺寸的图标
    images = []
    
    for size in sizes:
        # 创建画布
        img = Image.new('RGBA', size, (255, 255, 255, 0))  # 透明背景
        
        # 创建绘图对象
        draw = ImageDraw.Draw(img)
        
        # 计算器主体（圆角矩形）
        margin = size[0] // 10
        body_coords = [
            margin, margin,
            size[0] - margin, size[0] - margin
        ]
        
        # 主体颜色 - 蓝色渐变
        if size[0] >= 48:
            # 大尺寸图标添加渐变
            for y in range(margin, size[1] - margin):
                # 计算渐变颜色
                ratio = (y - margin) / (size[1] - 2 * margin)
                r = int(70 + ratio * 50)  # 70-120
                g = int(130 + ratio * 50)  # 130-180
                b = int(255)
                color = (r, g, b, 255)
                
                # 绘制水平线
                draw.line([(margin, y), (size[0] - margin, y)], fill=color, width=1)
        else:
            # 小尺寸图标使用纯色
            draw.rounded_rectangle(body_coords, radius=size[0]//8, 
                                 fill=(100, 150, 255, 255), outline=(80, 130, 235, 255), width=2)
        
        # 显示区域（顶部矩形）
        if size[0] >= 32:
            display_height = size[1] // 3
            display_coords = [
                margin * 2, margin * 2,
                size[0] - margin * 2, margin * 2 + display_height
            ]
            draw.rectangle(display_coords, fill=(240, 240, 245, 255), 
                          outline=(200, 200, 210, 255), width=1)
        
        # 按钮
        if size[0] >= 48:
            # 大图标绘制按钮
            button_size = size[0] // 6
            button_margin = size[0] // 12
            
            # 按钮颜色
            button_colors = [
                (255, 150, 0, 255),  # 橙色操作按钮
                (180, 180, 180, 255),  # 灰色功能按钮
                (220, 220, 220, 255)   # 浅灰数字按钮
            ]
            
            # 绘制几个示例按钮
            for i in range(3):
                x = size[0] // 2 + (i - 1) * (button_size + button_margin)
                y = size[1] * 2 // 3
                
                # 选择颜色
                color_index = min(i, len(button_colors) - 1)
                
                # 绘制按钮
                button_coords = [
                    x - button_size // 2, y - button_size // 2,
                    x + button_size // 2, y + button_size // 2
                ]
                draw.rounded_rectangle(button_coords, radius=button_size//4,
                                     fill=button_colors[color_index])
        
        # 添加文字（仅在足够大的图标上）
        if size[0] >= 64:
            try:
                # 尝试使用系统字体
                font_size = size[0] // 4
                
                # 尝试几种字体
                font_paths = [
                    "C:/Windows/Fonts/arial.ttf",
                    "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
                    "C:/Windows/Fonts/simhei.ttf",  # 黑体
                ]
                
                font = None
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        try:
                            font = ImageFont.truetype(font_path, font_size)
                            break
                        except:
                            continue
                
                if font:
                    # 绘制"Calc"文字
                    text = "C" if size[0] <= 128 else "Calc"
                    text_bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                    
                    text_x = (size[0] - text_width) // 2
                    text_y = (size[1] - text_height) // 2
                    
                    draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
            except:
                pass  # 如果添加文字失败，继续
        
        images.append(img)
    
    # 保存为ICO文件
    output_path = "calculator.ico"
    images[0].save(
        output_path,
        format='ICO',
        sizes=[(img.width, img.height) for img in images],
        append_images=images[1:]
    )
    
    print(f"✓ 图标已生成: {output_path}")
    print(f"✓ 图标尺寸: {sizes}")
    
    # 预览图标
    try:
        images[-1].save("icon_preview.png")
        print(f"✓ 预览图已保存: icon_preview.png")
        
        # 显示预览（可选）
        show_preview = input("是否显示图标预览？(y/n): ").strip().lower()
        if show_preview == 'y':
            images[-1].show()
    except:
        pass
    
    return output_path

def create_simple_icon():
    """创建简单图标（如果上面的太复杂）"""
    print("正在生成简单图标...")
    
    # 简单的单尺寸图标
    size = (256, 256)
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 蓝色圆角矩形背景
    draw.rounded_rectangle([20, 20, 236, 236], radius=40, 
                         fill=(100, 150, 255, 255), 
                         outline=(80, 130, 235, 255), width=10)
    
    # 白色计算器符号
    # 绘制显示屏
    draw.rectangle([60, 60, 196, 110], fill=(240, 240, 245, 255), 
                  outline=(200, 200, 210, 255), width=3)
    
    # 绘制按钮
    button_positions = [
        (90, 150), (150, 150), (210, 150),
        (90, 190), (150, 190), (210, 190),
        (90, 230), (150, 230), (210, 230),
    ]
    
    for i, (x, y) in enumerate(button_positions):
        # 按钮样式
        if i == 2:  # 操作按钮（橙色）
            color = (255, 150, 0, 255)
        elif i == 0:  # 功能按钮（灰色）
            color = (180, 180, 180, 255)
        else:  # 数字按钮（白色）
            color = (255, 255, 255, 255)
        
        draw.rounded_rectangle([x-15, y-15, x+15, y+15], radius=8, 
                             fill=color, outline=(200, 200, 200, 255), width=2)
    
    # 保存为多尺寸ICO
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = [img.resize(s, Image.Resampling.LANCZOS) for s in sizes]
    
    output_path = "calculator_simple.ico"
    images[0].save(
        output_path,
        format='ICO',
        sizes=sizes,
        append_images=images[1:]
    )
    
    print(f"✓ 简单图标已生成: {output_path}")
    
    # 保存预览
    img.save("icon_simple_preview.png")
    print(f"✓ 预览图已保存: icon_simple_preview.png")
    
    return output_path

def convert_image_to_icon(image_path):
    """将现有图片转换为图标"""
    if not os.path.exists(image_path):
        print(f"✗ 图片不存在: {image_path}")
        return None
    
    print(f"正在将图片转换为图标: {image_path}")
    
    try:
        # 打开图片
        img = Image.open(image_path)
        
        # 转换为RGBA（确保透明通道）
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # 需要的尺寸
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # 生成不同尺寸
        images = [img.resize(s, Image.Resampling.LANCZOS) for s in sizes]
        
        # 保存为ICO
        output_path = "calculator_from_image.ico"
        images[0].save(
            output_path,
            format='ICO',
            sizes=sizes,
            append_images=images[1:]
        )
        
        print(f"✓ 图标已生成: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"✗ 转换失败: {e}")
        return None

if __name__ == "__main__":
    print("=" * 50)
    print("计算器图标生成工具")
    print("=" * 50)
    
    # 检查Pillow是否已安装
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("正在安装Pillow库...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
        from PIL import Image, ImageDraw, ImageFont
    
    while True:
        print("\n请选择图标生成方式:")
        print("1. 生成精美计算器图标")
        print("2. 生成简单计算器图标")
        print("3. 将现有图片转换为图标")
        print("4. 查看已存在的图标文件")
        print("5. 退出")
        
        choice = input("请输入选项 (1-5): ").strip()
        
        if choice == "1":
            create_calculator_icon()
        elif choice == "2":
            create_simple_icon()
        elif choice == "3":
            image_path = input("请输入图片路径: ").strip()
            if image_path:
                convert_image_to_icon(image_path)
        elif choice == "4":
            print("\n当前目录中的图标文件:")
            for file in os.listdir('.'):
                if file.endswith(('.ico', '.png', '.jpg', '.jpeg')):
                    size = os.path.getsize(file) if os.path.isfile(file) else 0
                    print(f"  - {file} ({size:,} bytes)")
        elif choice == "5":
            print("再见！")
            break
        else:
            print("无效选项，请重新输入")